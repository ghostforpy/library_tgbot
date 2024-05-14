from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


from tgbot.utils import fill_file_id, send_photo, _get_file_id


class tgGroups(models.Model):
    name = models.CharField(
        "Группа пользователей", unique=False, max_length=150, blank=False
    )
    chat_id = models.BigIntegerField("ИД чата в Телеграм", null=True)
    link = models.CharField(
        "Ссылка на группу", unique=False, max_length=150, blank=True, null=True
    )
    text = models.TextField("Описание группыt", blank=True, null=True)
    for_all_users = models.BooleanField("Для всех пользователей", default=False)
    file = models.FileField("Фото/Видео", blank=True, null=True, upload_to="events")
    file_id = models.CharField(
        "file_id", unique=False, max_length=255, blank=True, null=True
    )
    show_for_users = models.BooleanField("Показывать пользователям", default=False)
    send_new_users = models.BooleanField(
        "Отправлять сообщения о новых пользователях", default=False
    )
    send_advertisements = models.BooleanField(
        "Отправлять сообщения о рекламных сообщениях", default=False
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs) -> None:
        if self.file:
            file_ext = self.file.name.split(".")[-1]
        else:
            file_ext = ""
        if file_ext in ["jpg", "jpeg", "png", "gif", "tif", "tiff", "bmp"]:
            mess = send_photo(settings.TRASH_GROUP, self.file, caption="")
            file_id, _ = _get_file_id(mess)
            self.file_id = file_id
        else:
            self.file_id = ""
            self.file = ""
        return super().save(*args, **kwargs)

    @classmethod
    def get_group_by_name(cls, gr_name: str) -> "tgGroups":
        return cls.objects.filter(name=gr_name).first()

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.pk,),
        )

    class Meta:
        verbose_name_plural = _("Telegram чаты")
        verbose_name = _("Telegram чат")
        ordering = ["name"]


class UsertgGroups(models.Model):
    group = models.ForeignKey(tgGroups, on_delete=models.CASCADE, verbose_name="Группа")
    user = models.ForeignKey(
        "User", on_delete=models.CASCADE, verbose_name="Пользователь"
    )

    def __str__(self):
        return str(self.group)

    class Meta:
        verbose_name_plural = "Группы пользователя"
        verbose_name = "Группа пользователя"
        ordering = ["user", "group"]
