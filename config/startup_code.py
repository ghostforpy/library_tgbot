import datetime
import os
import traceback

from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.conf import settings

from tgbot.models import tgGroups
from sheduler.models import MessageTemplates

from config.constants import *


try:
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/messages"):
        os.mkdir(f"{settings.MEDIA_ROOT}/messages")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/user_fotos"):
        os.mkdir(f"{settings.MEDIA_ROOT}/user_fotos")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/downloads"):
        os.mkdir(f"{settings.MEDIA_ROOT}/downloads")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/task_attachement"):
        os.mkdir(f"{settings.MEDIA_ROOT}/task_attachement")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/task_attachement/images"):
        os.mkdir(f"{settings.MEDIA_ROOT}/task_attachement/images")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/task_attachement/files"):
        os.mkdir(f"{settings.MEDIA_ROOT}/task_attachement/files")
    if not os.path.isdir(f"{settings.MEDIA_ROOT}/books_files"):
        os.mkdir(f"{settings.MEDIA_ROOT}/books_files")

    tg_group = tgGroups.objects.filter(name="Администраторы").first()
    if not tg_group and settings.ADMIN_GROUP:
        tg_group = tgGroups(name="Администраторы", chat_id=settings.ADMIN_GROUP)
        tg_group.save()

    # задача рассылки сообщений
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=10,
        period=IntervalSchedule.SECONDS,
    )
    task, created = PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Рассылка запланированных сообщений",
        task="msg.send_message",
    )

    # create message templates
    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.REG_REMINDER
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.REG_REMINDER
        template.name = "Шаблон для напоминаний о продолжении регистрации"
        template.text = 'Вы не завершили регистрацию в боте. Для завершения регистрации нажмите "Продолжить".'
        template.language = "RU"
        template.save()

    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.HAPPY_BIRTHDAY
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.HAPPY_BIRTHDAY
        template.name = "Шаблон для поздравления с днем рождения"
        template.text = "BOT поздравляет вас с Днем рождения"
        template.language = "RU"
        template.save()

    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE
        template.name = "Шаблон для приветственного сообщения новому пользователю"
        template.text = (
            "Поздравляем! Вы успешно зарегистрировались в системе. "
            "Информация передана администраторам. "
            "Для использования полного набора функций Вам необходимо дождаться подтверждения регистрации. "
            "О подтверждении регистрации мы вам сообщим. А пока можете в профиле пользователя исправить введенные и заполнить дополнительные данные."
        )
        template.language = "RU"
        template.save()

    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.WELCOME_MESSAGE
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_MESSAGE
        template.name = (
            "Шаблон сообщения при начале работы для подтвержденного пользователя"
        )
        template.text = "Меню"
        template.language = "RU"
        template.save()

    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE
        template.name = "Шаблон сообщения при начале работы для неподдтвержденного(заблокированного) пользователя"
        template.text = "К сожалению Ваша учетная запись ещё заблокирована. Ожидайте проверки администратором."
        template.language = "RU"
        template.save()

    template = MessageTemplates.objects.filter(
        code=MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE
    ).first()
    if not template:
        template = MessageTemplates()
        template.code = MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE
        template.name = "Шаблон сообщения при начале работы для забаненого пользователя"
        template.text = (
            "К сожалению Вашу учетная запись забанили. "
            "Для выяснения причин свяжитесь с администраторами. Причина бана: \n"
        )
        template.language = "RU"
        template.save()

except Exception as exc:
    print("Can't load init data")
    print(exc)
    print(traceback.format_exc())
