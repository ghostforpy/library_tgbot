from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from django.conf import settings


from config.constants import MessageTemplatesCode

from sheduler.models import MessageTemplates

from tgbot.handlers.utils import (
    get_no_foto_id,
    send_mess_by_tmplt,
    fill_file_id,
    send_photo,
    send_message
)
from tgbot.handlers.keyboard import make_keyboard
from tgbot import utils
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import NO_ADMIN_GROUP, get_start_mess
from tgbot.models import User, NewUser, tgGroups

from .messages import *
from .answers import *


def end_registration(update:Update, context: CallbackContext, new_user: NewUser):
    user = User(user_id=new_user.user_id)
    user.username = new_user.username
    user.last_name = new_user.last_name
    user.first_name = new_user.first_name
    user.email = new_user.email
    user.telefon = new_user.telefon
    user.patronymic = new_user.patronymic
    user.date_of_birth = new_user.date_of_birth
    user.company = new_user.company
    user.language = new_user.language
    user.status = new_user.status
    user.site = new_user.site
    user.about = new_user.about
    user.created_at = new_user.created_at
    user.language_code = new_user.language_code
    user.is_blocked_bot = False
    user.comment = "Зарегистрирован"
    user.save()
    new_user.registered = True
    new_user.save()
    # пофиксить ========================
    user.main_photo = new_user.main_photo
    user.main_photo_id = new_user.main_photo_id
    user.save()
    if not user.main_photo_id and user.main_photo:
        fill_file_id(user, "main_photo")
    photo_id = user.main_photo_id
    if not photo_id:
        user.main_photo_id = photo_id = get_no_foto_id()
        user.save()
    # ============================
    
    profile_txt = user.full_profile(language=user.language)
    # utils.send_message(user.user_id, text=profile_txt)
    send_photo(user.user_id, photo_id, caption=profile_txt)

    # отправка приветственного сообщения
    mess_template = MessageTemplates.objects.get(code=MessageTemplatesCode.WELCOME_NEWUSER_MESSAGE)
    if user.language != mess_template.language and mess_template.foreingnamemessagetemplates_set.filter(language=user.language).exists():
        mess_template.text = mess_template.foreingnamemessagetemplates_set.filter(language=user.language).first().translate
    send_mess_by_tmplt(user.user_id, mess_template, reply_markup=ReplyKeyboardRemove()) 

    send_message(
                user_id=user.user_id,
                text=get_start_mess(user),
                reply_markup=get_start_menu(user)
            )

    # отправка сообщения в группу администраторов
    group = tgGroups.get_group_by_name("Администраторы")
    # if (group == None) or (group.chat_id == 0):
    #     update.message.reply_text(NO_ADMIN_GROUP)
    if group:
        domain = settings.DOMAIN
        if settings.DEBUG:
            domain = 'http://0.0.0.0:8000'
        bn = {f"manage_new_user-{user.user_id}":"Посмотреть пользователя"}
        reply_markup =  make_keyboard(bn,"inline",1)
        text =f"Зарегистрирован новый пользователь @{utils.mystr(user.username)} {user.first_name} {utils.mystr(user.last_name)}\n"
        text += f'{domain}{user.get_admin_url()}'
        send_message(group.chat_id, text, reply_markup =  reply_markup)
    context.user_data.clear()
    return ConversationHandler.END