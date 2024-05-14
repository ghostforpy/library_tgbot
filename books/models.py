import telegram

from django.db import models
from django.utils.translation import gettext_lazy as _

# from django.utils.translation import override as translation_override
from django.conf import settings
from django.core.exceptions import ValidationError
from tgbot.utils import send_document, _get_file_id


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
    progress_txt = models.FloatField(
        "Прогресс", default=0.0, help_text="Для книг типа TXT"
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name_plural = "Прогрессы"
        verbose_name = "Прогресс"

    @property
    def progress(self):
        if self.book.book_type == "txt":
            return f"{self.progress_txt}%"
        else:
            return "not supported"
