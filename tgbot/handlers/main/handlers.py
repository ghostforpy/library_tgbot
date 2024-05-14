from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    # ConversationHandler,
)
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override
from .messages import *
from .answers import *
from tgbot.my_telegram.conversationhandler import (
    MyConversationHandler as ConversationHandler,
)
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.utils import extract_user_data_from_update, mystr, send_contact, send_message
import tgbot.models as mymodels


# Обработка отправки сообщений
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(
        SENDING_CANCELED, reply_markup=make_keyboard(EMPTY, "usual", 1)
    )
    command_start(update, context)
    return ConversationHandler.END


def start_conversation_affiliate(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    text = AFFILATE_MESS
    send_message(user_id=user.user_id, text=text)
    text = f"{context.bot.link}/?start={user_id}"
    send_message(user_id=user.user_id, text=text)

    return ConversationHandler.END


def start_contact_us(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    with translation_override(user.language):
        btns = {
            "handle_questions": _("Задать вопрос"),
            "handle_complaints": _("Жалоба"),
            "handle_suggestions": _("Предложение"),
        }
        kwargs = {
            "text": select_menu(),
            "reply_markup": make_keyboard(btns, "inline", 1, footer_buttons=back()),
        }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "working"


def handle_complaints(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    with translation_override(user.language):
        kwargs = {
            "text": complaints_mess(),
            "reply_markup": make_keyboard({}, "inline", 1, start_contact_us_btn()),
        }
    send_message(user_id, **kwargs)
    return "complaints"


def handle_suggestions(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    with translation_override(user.language):
        kwargs = {
            "text": suggestion_mess(),
            "reply_markup": make_keyboard({}, "inline", 1, start_contact_us_btn()),
        }
    send_message(user_id, **kwargs)
    return "suggestions"


def handle_questions(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query.answer()
    with translation_override(user.language):
        kwargs = {
            "text": question_mess(),
            "reply_markup": make_keyboard({}, "inline", 1, start_contact_us_btn()),
        }
    send_message(user_id, **kwargs)
    return "questions"


def enter_complaints(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    group = mymodels.tgGroups.get_group_by_name("Администраторы")
    if group:
        text = f"Пришла новая жалоба от @{mystr(user.username)}:\n"
        text += f'"{update.message.text}"'
        send_message(group.chat_id, text)
        if not user.username:
            send_contact(
                user_id=group.chat_id,
                phone_number=user.telefon,
                first_name=user.first_name,
                last_name=user.last_name,
            )
    with translation_override(user.language):
        text = _("Ваша жалоба отправлена")
    send_message(user_id=user.user_id, text=text)
    command_start(update, context)
    return ConversationHandler.END


def enter_suggestions(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    group = mymodels.tgGroups.get_group_by_name("Администраторы")
    if group:
        text = f"Пришло новое предложение от @{mystr(user.username)}:\n"
        text += f'"{update.message.text}"'
        send_message(group.chat_id, text)
        if not user.username:
            send_contact(
                user_id=group.chat_id,
                phone_number=user.telefon,
                first_name=user.first_name,
                last_name=user.last_name,
            )
    with translation_override(user.language):
        text = _("Ваше предложение отправлено")
    send_message(user_id=user.user_id, text=text)
    command_start(update, context)
    return ConversationHandler.END


def enter_questions(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    group = mymodels.tgGroups.get_group_by_name("Администраторы")
    if group:
        text = f"Пришлёл новый вопрос от @{mystr(user.username)}:\n"
        text += f'"{update.message.text}"'
        send_message(group.chat_id, text)
        if not user.username:
            send_contact(
                user_id=group.chat_id,
                phone_number=user.telefon,
                first_name=user.first_name,
                last_name=user.last_name,
            )
    with translation_override(user.language):
        text = _("Ваш вопрос отправлен")
    send_message(user_id=user.user_id, text=text)
    command_start(update, context)
    return ConversationHandler.END


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    # conv_handler_send_mess = ConversationHandler( # здесь строится логика разговора
    #     # точка входа в разговор
    #     entry_points=[
    #                  CallbackQueryHandler(start_conversation_affiliate, pattern="^affiliate$")
    #                   ],
    #     # этапы разговора, каждый со своим списком обработчиков сообщений
    #     states={
    #         # "sending":[MessageHandler(Filters.text & FilterPrivateNoCommand, sending_mess)],
    #     },
    #     # точка выхода из разговора
    #     fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
    #                CommandHandler('start', stop_conversation, Filters.chat_type.private)],
    # )
    # Диалог жалоб и предложений
    complaints_and_suggestions = ConversationHandler(  # здесь строится логика разговора
        # точка входа в разговор
        entry_points=[
            CallbackQueryHandler(start_contact_us, pattern="^contact_us$"),
            CallbackQueryHandler(handle_complaints, pattern="^handle_complaints$"),
            CallbackQueryHandler(handle_suggestions, pattern="^handle_suggestions$"),
            CallbackQueryHandler(handle_questions, pattern="^handle_questions$"),
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working": [
                CallbackQueryHandler(handle_complaints, pattern="^handle_complaints$"),
                CallbackQueryHandler(
                    handle_suggestions, pattern="^handle_suggestions$"
                ),
                CallbackQueryHandler(handle_questions, pattern="^handle_questions$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, start_contact_us),
            ],
            "complaints": [
                MessageHandler(Filters.text & FilterPrivateNoCommand, enter_complaints),
                CallbackQueryHandler(start_contact_us, pattern="^start_contact_us$"),
            ],
            "suggestions": [
                MessageHandler(
                    Filters.text & FilterPrivateNoCommand, enter_suggestions
                ),
                CallbackQueryHandler(start_contact_us, pattern="^start_contact_us$"),
            ],
            "questions": [
                MessageHandler(Filters.text & FilterPrivateNoCommand, enter_questions),
                CallbackQueryHandler(start_contact_us, pattern="^start_contact_us$"),
            ],
        },
        # точка выхода из разговора
        fallbacks=[
            CommandHandler("cancel", stop_conversation, Filters.chat_type.private),
            CommandHandler("start", stop_conversation, Filters.chat_type.private),
        ],
    )
    # dp.add_handler(conv_handler_send_mess)
    dp.add_handler(complaints_and_suggestions)
