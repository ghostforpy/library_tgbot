import re
import telegram

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

    class Meta:
        verbose_name_plural = "Книги"
        verbose_name = "Книга"

    def __str__(self) -> str:
        r = self.title
        if self.author:
            r = f"{r} ({self.author})"
        return r

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

    def read_txt_book(self):
        key = f"book_{self.id}"
        text = cache.get(key)
        if text is None:
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

    # def read_txt_book(self):
    #     with self.file.file.open() as file:
    #         BookInLines = file.readlines()
    #     return BookInLines

    # def get_txt_book_frame(self, start_line, end_line):
    #     bookframe = "".join(self.read_txt_book()[start_line:end_line])
    #     bookframe = re.sub(r"\s{3,}", "\n~~~~~~\n", bookframe)
    #     return bookframe

    # @property
    # def get_txt_frame_len_next(self, current_progress):
    #     maxframe_len = len(
    #         self.get_txt_book_frame(current_progress, current_progress + 15)
    #     )
    #     if maxframe_len >= 4000:
    #         midframe_len = len(
    #             self.get_txt_book_frame(current_progress, current_progress + 10)
    #         )
    #         if midframe_len >= 4000:
    #             lowframe_len = len(
    #                 self.get_txt_book_frame(current_progress, current_progress + 5)
    #             )
    #             if lowframe_len >= 4000:
    #                 return 1
    #             else:
    #                 return 5
    #         else:
    #             return 10
    #     else:
    #         return 15

    # @property
    # def get_txt_frame_len_prev(self, current_progress):
    #     maxframe_len = len(
    #         self.get_txt_book_frame(current_progress - 15, current_progress)
    #     )
    #     if maxframe_len >= 4000:
    #         midframe_len = len(
    #             self.get_txt_book_frame(current_progress - 10, current_progress)
    #         )
    #         if midframe_len >= 4000:
    #             lowframe_len = len(
    #                 self.get_txt_book_frame(current_progress - 5, current_progress)
    #             )
    #             if lowframe_len >= 4000:
    #                 return 1
    #             else:
    #                 return 5
    #         else:
    #             return 10
    #     else:
    #         return 15

    # @property
    # def check_txt_if_end(self, current_progress):
    #     book_len = len(self.get_txt_book_frame(0, -1))
    #     dif = abs(
    #         len(
    #             self.get_txt_book_frame(
    #                 0, current_progress + self.get_txt_frame_len_next(current_progress)
    #             )
    #         )
    #         - book_len
    #     )
    #     relative_dif = (dif / book_len) * 100
    #     return relative_dif <= 0.018


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
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name_plural = "Прогрессы"
        verbose_name = "Прогресс"

    @property
    def progress(self):
        if self.book.book_type == "txt":
            return "{:.2%}".format(self.progress_txt / self.total_pages_txt_book)
        else:
            return "not supported"
