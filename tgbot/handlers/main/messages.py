from django.utils.translation import gettext as _

from tgbot.models import User
from sheduler.models import MessageTemplates
from config.constants import MessageTemplatesCode

ASK_REENTER = "Пожалуйста, используйте доступные пункты меню."  

# Стартовый диалог
WELCOME = "Добрый день! Вы находитесь в Telegram боте. \n" \
          "Используйте кнопки меню для работы с ботом." 
AFFILATE_MESS = "Если вы хотите видеть своего коллегу/партнера/друга в нашем сообществе "\
                "и готовы его рекомендовать и ручаться, перешлите ему ссылку-приглашение. " \
                "Если он пройдет по ней регистрацию, то Вы будете указаны у него в рекомендателях."
COMPLAINTS_AND_SUGGESTIONS_MESS = {
    "RU": "Выберите пункт меню",
    "EN": "Select a menu item",
    "UZ": "Menyu",
}
select_menu = lambda: _("Выберите пункт меню")
complaints_mess = lambda: _("Введите текст жалобы")
suggestion_mess = lambda: _("Введите текст предложения")
question_mess = lambda: _("Введите текст вопроса")
back_btn = lambda: "⬅️ " + _("Назад")
back = lambda: {"start": back_btn()}
start_contact_us_btn = lambda: {"start_contact_us": back_btn()}

def get_start_mess(user: User):
    if user.is_banned:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_BANNED_USR_MESSAGE)
        res = mess_template.text + user.comment
    elif not user.verified_by_admin:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_BLOCKERD_USR_MESSAGE)
        res =  mess_template.text
        f_mess_template = mess_template.foreingnamemessagetemplates_set.filter(language=user.language).first()
        if user.language != mess_template.language:
            if f_mess_template:
                res = f_mess_template.translate
    else:
        mess_template = MessageTemplates.objects.get(code = MessageTemplatesCode.WELCOME_MESSAGE)
        res =  mess_template.text
        f_mess_template = mess_template.foreingnamemessagetemplates_set.filter(language=user.language).first()
        if user.language != mess_template.language:
            if f_mess_template:
                res = f_mess_template.translate


    if not user.username:
        res += "\n<b>" + _("У Вас в Телеграм не введено имя пользователя. " \
               "Это может затруднить общение с вами. Введите его в настройках Телеграм") + "</b>"
    if not user.status:
        res += "\n<b>" + _("Вам не присвоен статус пользователя. " \
               "Многие функции бота работать не будут. Сообщите об этом администраторам") + "</b>"

    return res 

# Отправка сообщения админам
SENDING_WELCOME = "Вы в режиме отправки сообщения администраторам"
SENDING_CANCELED = "Отправка сообщения отменена"
NO_ADMIN_GROUP = 'Группа "Администраторы" не найдена или не указан ее чат. Сообщите об ошибке'
ASK_MESS = "Введите текст сообщения"
MESS_SENDED = "Сообщение отослано"