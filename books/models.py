import re
from lxml import etree
import telegram

from django.urls import reverse
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import caches

# from django.utils.translation import override as translation_override
from django.conf import settings
from django.core.exceptions import ValidationError

from tgbot.utils import send_document, _get_file_id

from .utils import paginate_string

cache = caches["default"]


class Book(models.Model):
    title = models.CharField(_("Наименование"), max_length=150, null=True, blank=True)
    author = models.CharField(_("Автор"), max_length=50, null=True, blank=True)
    file = models.FileField("Файл книги", upload_to="books_files")
    file_id = models.CharField("id файла книги", max_length=150, null=True, blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    user_upload = models.ForeignKey(
        "tgbot.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_books",
        verbose_name="Загрузивший",
    )
    book_type = models.CharField(
        "Тип книги",
        default="txt",
        choices=[("txt", "txt"), ("fb2", "fb2")],
        max_length=10,
    )
    encoding = models.CharField(
        _("Кодировка"), null=True, blank=True, default="", max_length=30
    )

    class Meta:
        verbose_name_plural = "Книги"
        verbose_name = "Книга"

    def __str__(self) -> str:
        r = self.title
        if self.author:
            r = f"{r} ({self.author})"
        return r

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.id,),
        )

    def clean(self):
        def fill_file_id():
            mess = send_document(
                settings.TRASH_GROUP,
                self.file,
            )
            if type(mess) != telegram.message.Message:
                raise ValidationError(
                    {
                        "file": "Тип не соответствует",
                    }
                )
            file_id, _ = _get_file_id(mess)
            self.file_id = file_id

        if self.file:
            file_ext = self.file.name.split(".")[-1]
        else:
            file_ext = ""
        if file_ext:
            if self.pk:
                file = Book.objects.get(pk=self.pk).file
                if file:
                    if self.file.size != file.size:
                        fill_file_id()
                else:
                    fill_file_id()
            else:
                fill_file_id()
        else:
            self.file_id = ""
            self.file = ""
        return super().clean()

    # @property
    # def get_page_book_txt(self, page_num):
    #     p = Paginator(self.get_paginated_book_txt(), 1)
    #     page = p.page(page_num)
    #     return page[0],

    def read_txt_book(self, from_cache=True):
        key = f"book_{self.id}"
        text = cache.get(key)
        if text is None or not from_cache:
            with self.file.file.open() as file:
                text = file.read().decode()
            text = re.sub(r"\n{1,}", "\n", text)
            cache.set(key, text, 3 * 60)  # 3 min
        return text

    def get_paginated_book_txt(self):
        key = f"paginated_book_{self.id}"
        book_pages = cache.get(key)
        if book_pages is None:
            book_pages = paginate_string(self.read_txt_book())
            cache.set(key, book_pages, 3 * 60)  # 3 min
        return book_pages

    def read_fb2_book(self, from_cache=True):
        key = f"book_{self.id}"
        text = cache.get(key)
        if text is None or not from_cache:
            with self.file.file.open() as file:
                text = file.read().decode(self.encoding)
            cache.set(key, text, 3 * 60)  # 3 min
        et = etree.fromstring(text.encode(self.encoding))
        return et

    def get_chapters_fb2_book(self):
        book = self.read_fb2_book()
        return book.findall("*//section", namespaces=book.nsmap)

    def get_titles_fb2_book(self):
        text = _("Глава")
        sections = self.get_chapters_fb2_book()
        titles = list()
        for idx, __ in enumerate(sections, start=1):
            titles.append(f"{text} {idx}")
        return titles

    def get_chapter_book_fb2(self, chapter_num):
        chapters = self.get_chapters_fb2_book()
        chapter = chapters[chapter_num - 1]
        return "\n".join(
            [i.text for i in chapter.findall("./p", namespaces=chapter.nsmap) if i.text]
        )

    def get_paginated_chapter_book_fb2(self, chapter_num):
        key = f"paginated_book_{self.id}_{chapter_num}"
        chapter_book_pages = cache.get(key)
        if chapter_book_pages is None:
            chapter_book_pages = paginate_string(self.get_chapter_book_fb2(chapter_num))
            cache.set(key, chapter_book_pages, 3 * 60)  # 3 min
        return chapter_book_pages


class UserBookProgress(models.Model):
    user = models.ForeignKey(
        "tgbot.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="readed_books",
        verbose_name="Пользователь",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user_progresses",
        verbose_name="Книга",
    )
    progress_txt = models.IntegerField(
        "Прогресс", default=1, help_text="Для книг типа TXT"
    )
    total_pages_txt_book = models.IntegerField(
        "Общее количество страниц", default=1, help_text="Для книг типа TXT"
    )
    progress_section_fb_book = models.IntegerField(
        "Прогресс глав", default=1, help_text="Для книг типа FB2"
    )
    total_sections_fb_book = models.IntegerField(
        "Общее количество глав", default=1, help_text="Для книг типа FB2"
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name_plural = "Прогрессы"
        verbose_name = "Прогресс"

    @property
    def progress(self):
        if self.book.book_type == "txt":
            return "{:.2%}".format(self.progress_txt / self.total_pages_txt_book)
        elif self.book.book_type == "fb2":
            section = (
                _("Глава")
                + f" {self.progress_section_fb_book}/{self.total_sections_fb_book}"
            )
            return "{} - {:.2%}".format(
                section, self.progress_txt / self.total_pages_txt_book
            )
        else:
            return "not supported"
