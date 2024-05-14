# -*- coding: utf-8 -*-

import logging

import telegram
from telegram.update import Update
from telegram.constants import CHAT_CHANNEL, CHAT_GROUP, CHAT_SUPERGROUP
from telegram.ext.callbackcontext import CallbackContext

# from telegram.ext import ConversationHandler
from tgbot.my_telegram.conversationhandler import (
    MyConversationHandler as ConversationHandler,
)
from telegram.error import BadRequest
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override
from django.core.cache import caches
from django.conf import settings

from tgbot.models import User, NewUser, tgGroups
from tgbot.utils import extract_user_data_from_update, send_message
from tgbot.handlers.utils import handler_logging
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.registration.messages import registration_start_mess
from tgbot.handlers.registration.answers import registration_start_btn
from tgbot.handlers.main.answers import EMPTY, get_start_menu
from tgbot.handlers.main.messages import get_start_mess


conv_cache = caches["conversations"]

logger = logging.getLogger("default")
logger.info("Command handlers check!")


def clear_conv_states(user_id):
    l = [user_id]
    conv_cache.delete(tuple(l))
    l.append(user_id)
    conv_cache.delete(tuple(l))
    l.append(user_id)
    conv_cache.delete(tuple(l))


# @handler_logging()
def command_start(update: Update, context: CallbackContext):
    context.user_data.clear()
    userdata = extract_user_data_from_update(update)
    context.user_data.update(userdata)
    user_id = userdata["user_id"]
    # clear conversations
    clear_conv_states(user_id)

    user = User.objects.annotate_available_functions().get_user_by_username_or_user_id(
        user_id
    )

    if user != None:
        if user.username != userdata.get("username"):
            user.username = userdata.get("username")
            user.save()

    if user == None:
        language_code = userdata.get("language_code")
        if language_code.upper() in [i[0] for i in NewUser.LANGUAGE]:
            language = language_code.upper()
        else:
            language = "RU"
        context.user_data["language"] = language
        languages = {item[0]: item[1] for item in NewUser.LANGUAGE}
        language = context.user_data.get("language", NewUser.DEFAULT_LANGUAGE)
        ASK_LANGUAGE = {
            "UZ": "Tilni tanlang",
            "RU": "Выберите язык",
            # "EN": "Select a language",
        }
        kwargs = {
            "text": ASK_LANGUAGE[language],
            "reply_markup": make_keyboard(languages, "inline", 1),
        }
        if update.message is not None:
            update.message.reply_text(**kwargs)
        elif update.callback_query is not None:
            update.callback_query.answer()
            try:
                update.callback_query.edit_message_text(**kwargs)
            except BadRequest:
                send_message(user_id=update.callback_query.from_user.id, **kwargs)
    else:
        kwargs = {"text": get_start_mess(user), "reply_markup": get_start_menu(user)}
        if update.message != None:
            update.message.reply_text(**kwargs, parse_mode=telegram.ParseMode.HTML)
        elif update.callback_query != None:
            update.callback_query.answer()
            try:
                update.callback_query.edit_message_text(
                    **kwargs, parse_mode=telegram.ParseMode.HTML
                )
            except BadRequest:
                send_message(user_id=update.callback_query.from_user.id, **kwargs)
    # clear_conversation(context.dispatcher.handlers[0], user_id)
    return ConversationHandler.END


def choose_lang(update: Update, context: CallbackContext):
    update.callback_query.answer()
    userdata = extract_user_data_from_update(update)
    user_id = userdata["user_id"]
    new_user = NewUser.objects.filter(user_id=user_id).first()
    if not new_user:
        new_user = NewUser(user_id=user_id)
    new_user.username = userdata.get("username")
    new_user.first_name = userdata.get("first_name")
    new_user.last_name = userdata.get("last_name")
    new_user.language_code = userdata.get("language_code")
    new_user.language = update.callback_query.data
    # if new_user.language_code.upper() in [i[0] for i in NewUser.LANGUAGE]:
    #     new_user.language = new_user.language_code.upper()
    # context.user_data["language"] = new_user.language

    new_user.save()
    with translation_override(new_user.language):
        if update.message != None:
            update.message.reply_text(
                registration_start_mess(
                    f"{new_user.username}, " if new_user.username else ""
                ),
                reply_markup=make_keyboard(registration_start_btn(), "inline", 2),
            )
        elif update.callback_query != None:
            send_message(
                user_id=update.callback_query.from_user.id,
                text=registration_start_mess(
                    f"{new_user.username}, " if new_user.username else ""
                ),
                reply_markup=make_keyboard(registration_start_btn(), "inline", 2),
            )


def clear_conversation(handlers, user_id):
    for handler in handlers:
        h_type = type(handler)
        if isinstance(handler, ConversationHandler):
            handler.conversations.pop((user_id, user_id), 1)
            g = 1
        # context._dispatcher.handlers[0][11].conversations


def command_get_chat_id(update: Update, context: CallbackContext):
    userdata = extract_user_data_from_update(update)
    user_id = userdata["user_id"]

    user = User.objects.get_user_by_username_or_user_id(user_id)

    chat_id = update.effective_chat.id
    if user is not None:
        if user.is_admin:
            if update.effective_chat.type in [
                CHAT_CHANNEL,
                CHAT_GROUP,
                CHAT_SUPERGROUP,
            ]:
                group = tgGroups.objects.filter(chat_id=chat_id).first()
                if not group:
                    chat = update.effective_message.bot.get_chat(chat_id=chat_id)
                    group = tgGroups.objects.create(
                        name=chat.title,
                        chat_id=chat_id,
                        link=chat.invite_link,
                        text=chat.bio,
                    )
                    text = f"Создана новая группа {group.name}\n"
                else:
                    text = f"Группа {group.name} уже зарегистрирована\n"
                domain = settings.DOMAIN
                if settings.DEBUG:
                    domain = "http://0.0.0.0:8000"

                text += f"{domain}{group.get_admin_url()}"
                send_message(group.chat_id, text)

    send_message(
        user_id=chat_id,
        text=f"Chat ID: {chat_id}",
    )
