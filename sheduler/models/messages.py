from django.db import models
from django.utils.translation import gettext_lazy as _

from tgbot.models import User
from tgbot.models.language import LANGUAGE, DEFAULT_LANGUAGE


class MessagesToSend(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="receiver", verbose_name="Получатель", blank=True, null=True)    
    receiver_user_id = models.BigIntegerField("ID пользователя", blank=True, null=True)
    text = models.TextField("Текст сообщения", null=False, blank=False)
    created_at = models.DateTimeField("Создано в", auto_now_add=True)
    sended_at = models.DateTimeField("Отослано в", blank=True, null=True)
    sended = models.BooleanField("Отослано", default=False)
    file = models.FileField("Файл", blank=True, null=True, upload_to="messages")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    reply_markup = models.JSONField(blank=True, null = True) # здесь хранится словарь с описанием клавиатуры прикрепляемой к сообщению
    comment = models.TextField("Комментарий", blank=True, null=True)
    def __str__(self):
        return self.text
    class Meta:
        verbose_name_plural = 'Сообщения к отсылке' 
        verbose_name = 'Сообщение к отсылке' 
        ordering = ['created_at']


class MessageTemplates(models.Model):
    LANGUAGE = LANGUAGE
    DEFAULT_LANGUAGE = DEFAULT_LANGUAGE

    code = models.CharField("Код", max_length=256, null=False, blank=False)
    name = models.CharField("Название", max_length=256, null=False, blank=False)
    text = models.TextField("Текст сообщения", blank=False)
    file = models.FileField("Файл", blank=True, null=True, upload_to="templates")
    file_id = models.CharField("file_id", unique=False, max_length=255, blank=True, null = True)
    language = models.CharField(
        _("Язык"),
        max_length=50,
        default=DEFAULT_LANGUAGE,
        choices=LANGUAGE
    )

    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural = 'Шаблоны сообщений' 
        verbose_name = 'Шаблон сообщения' 
        ordering = ['code']


class ForeingNameMessageTemplates(models.Model):
    LANGUAGE = LANGUAGE
    DEFAULT_LANGUAGE = DEFAULT_LANGUAGE

    message_template = models.ForeignKey(
        MessageTemplates, 
        on_delete=models.CASCADE
    )
    translate = models.TextField("Перевод")
    language = models.CharField(
        _("Язык"),
        max_length=50,
        default=DEFAULT_LANGUAGE,
        choices=LANGUAGE
    )

    def __str__(self):
        return f'{self.language} {self.message_template}'

    class Meta:
        verbose_name_plural = 'Переводы шаблонов сообщений' 
        verbose_name = 'Перевод шаблона сообщения' 
        ordering = ['id']