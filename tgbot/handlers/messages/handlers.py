from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
)
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override

from config.constants import StatusCode
from sheduler.models.messages import MessagesToSend
from .messages import *
from .answers import *
from tgbot.my_telegram.conversationhandler import MyConversationHandler as ConversationHandler
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.main.messages import select_menu, back
from tgbot.utils import send_message
import tgbot.models as mymodels


# Обработка отправки сообщений
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END


def start_send_messages(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    with translation_override(user.language):
        btns = {
                "messages_to_all": _("Всем сотрудникам"),
            }
        if user.status.code not in [
            StatusCode.OWNER,
            StatusCode.DIRECTOR,
            StatusCode.ASSOCIATE_DIRECTOR
        ]:
            btns = {}
        kwargs = {
            "text": select_menu(),
            "reply_markup": make_keyboard(btns,"inline",1, footer_buttons=back())
        }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "working"

def blank(update: Update, context: CallbackContext):
    pass

def prepare_for_handle_message(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    with translation_override(user.language):
        kwargs = {
            "text": enter_message_text(),
            "reply_markup": make_keyboard({},"inline",1, footer_buttons=start_send_messages_btn())
        }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)

# def messages_to_agents(update: Update, context: CallbackContext):
#     prepare_for_handle_message(update, context)
#     return "messages_to_agents"

# def messages_to_supervisers(update: Update, context: CallbackContext):
#     prepare_for_handle_message(update, context)
#     return "messages_to_supervisers"

def messages_to_all(update: Update, context: CallbackContext):
    prepare_for_handle_message(update, context)
    return "messages_to_all"

def create_message_to_send(users, message, from_user):
    new_messages = []
    for _user in users:
        with translation_override(_user.language):
            text = message_from(str(from_user), message)
        new_mess = MessagesToSend(receiver=_user, text=text)
        new_messages.append(new_mess)
    MessagesToSend.objects.bulk_create(new_messages)
    with translation_override(from_user.language):
        send_message(from_user.user_id, text=message_sent())

# def handle_messages_to_agents(update: Update, context: CallbackContext):
#     if update.message:
#         user_id = update.message.from_user.id
#     else:
#         query = update.callback_query
#         user_id = query.from_user.id
#         query.answer()
#     user = mymodels.User.get_user_by_username_or_user_id(user_id)
#     if user.status.code == StatusCode.SUPERVISOR:
#         agents = Agent.objects.filter(user__isnull=False, supervisor__user=user).select_related("user")
#     elif user.status.code in [
#         StatusCode.OWNER,
#         StatusCode.DIRECTOR,
#         StatusCode.ASSOCIATE_DIRECTOR
#     ]:
#         agents = Agent.objects.filter(user__isnull=False).select_related("user")
#     else:
#         agents = Agent.objects.none()
#     users = [i.user for i in agents]
#     create_message_to_send(users, update.message.text, user)
#     return start_send_messages(update, context)

# def handle_messages_to_supervisers(update: Update, context: CallbackContext):
#     if update.message:
#         user_id = update.message.from_user.id
#     else:
#         query = update.callback_query
#         user_id = query.from_user.id
#         query.answer()
#     user = mymodels.User.get_user_by_username_or_user_id(user_id)
#     if user.status.code in [
#         StatusCode.OWNER,
#         StatusCode.DIRECTOR,
#         StatusCode.ASSOCIATE_DIRECTOR
#     ]:
#         supervisors = Supervisor.objects.filter(user__isnull=False).select_related("user")
#     else:
#         supervisors = Supervisor.objects.none()
#     users = [i.user for i in supervisors]
#     create_message_to_send(users, update.message.text, user)
#     return start_send_messages(update, context)

def handle_messages_to_all(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    if user.status.code in [
        StatusCode.OWNER,
        StatusCode.DIRECTOR,
        StatusCode.ASSOCIATE_DIRECTOR
    ]:
        users = mymodels.User.objects.exclude(user_id=user.user_id)
    else:
        users = mymodels.User.objects.none()
    if user.status.code == StatusCode.DIRECTOR:
        users = users.exclude(status__code=StatusCode.OWNER)
    if user.status.code == StatusCode.ASSOCIATE_DIRECTOR:
        users = users.exclude(status__code__in=[StatusCode.OWNER, StatusCode.DIRECTOR])
    create_message_to_send(users, update.message.text, user)
    return start_send_messages(update, context)

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    messages_conv = ConversationHandler( # здесь строится логика разговора
        persistent=True,
        name="messages_conversation",
        conversation_timeout=60*60*12, # 12 hours
        # точка входа в разговор
        entry_points=[
                     CallbackQueryHandler(start_send_messages, pattern="^messages$"),
                      ],      
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                # CallbackQueryHandler(messages_to_agents, pattern="^messages_to_agents$"),
                # CallbackQueryHandler(messages_to_supervisers, pattern="^messages_to_supervisers$"),
                CallbackQueryHandler(messages_to_all, pattern="^messages_to_all$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
            ],
            # "messages_to_agents":[
            #     MessageHandler(Filters.text & FilterPrivateNoCommand, handle_messages_to_agents),
            #     CallbackQueryHandler(start_send_messages, pattern="^start_send_messages$"),
            # ],
            # "messages_to_supervisers":[
            #     MessageHandler(Filters.text & FilterPrivateNoCommand, handle_messages_to_supervisers),
            #     CallbackQueryHandler(start_send_messages, pattern="^start_send_messages$"),
            # ],
            "messages_to_all":[
                MessageHandler(Filters.text & FilterPrivateNoCommand, handle_messages_to_all),
                CallbackQueryHandler(start_send_messages, pattern="^start_send_messages$"),
            ],
        },
        # точка выхода из разговора
        fallbacks=[
            CallbackQueryHandler(stop_conversation, pattern="^start$"),
            CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
            CommandHandler('start', stop_conversation, Filters.chat_type.private)
        ],
    )
    dp.add_handler(messages_conv)