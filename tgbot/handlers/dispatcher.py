# -*- coding: utf-8 -*-

"""Telegram event handlers."""
# import logging
import pytz
import importlib
import os.path

import telegram

from telegram.ext import (
    Updater,
    Dispatcher,
    Filters,
    MessageHandler,
    # JobQueue,
    CommandHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    # ChosenInlineResultHandler, PollAnswerHandler,
    Defaults,
)

from python_telegram_bot_django_persistence.persistence import DjangoPersistence

from django.conf import settings

# from dtb.settings import TELEGRAM_TOKEN

from sentry_sdk import capture_exception, capture_message

from tgbot.handlers import commands
from tgbot.handlers.main.handlers import setup_dispatcher_conv as setup_dispatcher_main
from tgbot.handlers.profile.handlers import (
    setup_dispatcher_conv as setup_dispatcher_prof,
)
from tgbot.handlers.user_library_books.handlers import (
    setup_dispatcher_conv as setup_dispatcher_user_library_books,
)
from tgbot.handlers.messages.handlers import (
    setup_dispatcher_conv as setup_dispatcher_messages,
)

# from tgbot.handlers.manage_members.handlers import setup_dispatcher_conv as setup_dispatcher_manage_memb
from tgbot.handlers.answers import ERROR_TEXT
from telegram.update import Update
from telegram import BotCommand
from telegram.ext.callbackcontext import CallbackContext
from tgbot.models.language import LANGUAGE
from tgbot.utils import send_message


# Отладочный пререхватчик. Ловит все апдейты
# Когда основные хендлеры не ловят апдейт он ловится тут
# и можно узнать причину
def catch_all_updates(update: Update, context: CallbackContext):
    # logger = logging.getLogger('default')
    # logger.info(f"CATCH! {update}")
    pass


def catch_errors(update: Update, context: CallbackContext):
    if update:
        if update.message is not None:
            send_message(
                user_id=update.message.from_user.id,
                text=ERROR_TEXT,
                reply_markup=telegram.ReplyKeyboardRemove(),
            )
        elif update.callback_query is not None:
            send_message(
                user_id=update.callback_query.from_user.id,
                text=ERROR_TEXT,
                reply_markup=telegram.ReplyKeyboardRemove(),
            )
        if not settings.DEBUG:
            capture_exception(context.error)
            capture_message(str(update))
    elif not settings.DEBUG:
        if isinstance(context, CallbackContext):
            capture_exception(context.error)
        else:
            capture_exception(context)  # for handle event.exception Job
    if settings.DEBUG:
        if update:
            raise context.error
        else:
            raise context  # for raise event.exception Job


def setup_dispatcher(dp: Dispatcher):
    """
    Adding handlers for events from Telegram
    """

    dp.add_handler(
        CommandHandler("start", commands.command_start, Filters.chat_type.private)
    )
    dp.add_handler(CommandHandler("get_chat_id", commands.command_get_chat_id))

    setup_dispatcher_main(dp)  # заполнение обработчиков главного диалога
    setup_dispatcher_prof(dp)  # заполнение обработчиков работы с профайлом
    # setup_dispatcher_manage_memb(dp) #заполнение обработчиков работы с поиском
    setup_dispatcher_messages(dp)  # заполнение обработчиков работы с сообщениями
    setup_dispatcher_user_library_books(
        dp
    )  # заполнение обработчиков работы с библиотекой книг пользователя

    for app in settings.LOCAL_APPS:
        if os.path.isfile(f"{app}/tgbothandlers/setup_dp.py"):
            module = importlib.import_module(f"{app}.tgbothandlers.setup_dp")
            module.setup_dp(dp)

    dp.add_handler(
        MessageHandler(Filters.text & Filters.chat_type.private, commands.command_start)
    )
    dp.add_handler(
        CallbackQueryHandler(
            commands.choose_lang, pattern="|".join([f"^{i[0]}$" for i in LANGUAGE])
        )
    )
    dp.add_handler(CallbackQueryHandler(commands.command_start))
    dp.add_handler(CallbackQueryHandler(commands.command_start, pattern="^start"))
    if not settings.DEBUG:
        dp.add_error_handler(catch_errors)
    dp.add_handler(MessageHandler(None, catch_all_updates), group=2)
    dp.add_handler(CallbackQueryHandler(catch_all_updates), group=2)
    dp.add_handler(InlineQueryHandler(catch_all_updates), group=2)

    return dp


def run_pooling():

    defaults = Defaults(
        parse_mode=telegram.ParseMode.HTML, tzinfo=pytz.timezone("Europe/Moscow")
    )
    """ Run bot in pooling mode """
    updater = Updater(
        settings.TELEGRAM_TOKEN,
        use_context=True,
        defaults=defaults,
        persistence=DjangoPersistence(),
    )

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)
    # jq = updater.job_queue
    # restarts_tasks(jq)

    bot_info = telegram.Bot(settings.TELEGRAM_TOKEN).get_me()
    bot_link = f"https://t.me/" + bot_info["username"]

    print(f"Pooling of '{bot_link}' started")
    # global POLLING_IS_RUNNING
    # POLLING_IS_RUNNING = True
    updater.start_polling(timeout=123, drop_pending_updates=True, allowed_updates=[])
    updater.idle()


def process_telegram_event(update_json):
    update = telegram.Update.de_json(update_json, bot)
    # dispatcher.process_update(update)
    update_queue.put(update)


# Global variable - best way I found to init Telegram bot
bot = telegram.Bot(settings.TELEGRAM_TOKEN)
# dispatcher = setup_dispatcher(Dispatcher(bot, None, workers=4, use_context=True))
TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
bot.set_my_commands(
    [
        BotCommand("/cancel", "Cancel"),
        BotCommand("/start", "Start"),
        BotCommand("/get_chat_id", "Get Chat ID"),
    ]
)
update_queue = None

if not settings.DEBUG and settings.MAIN_CONTAINER:
    from queue import Queue
    from threading import Thread
    from telegram.ext import JobQueue

    update_queue = Queue()

    dispatcher = Dispatcher(
        bot, update_queue, workers=4, use_context=True, persistence=DjangoPersistence()
    )
    dispatcher = setup_dispatcher(dispatcher)
    jq = JobQueue()
    jq.set_dispatcher(dispatcher)
    # restarts_tasks(jq)
    thread = Thread(target=dispatcher.start, name="dispatcher")
    thread.start()

    bot.set_webhook(
        url=f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook?url={settings.TELEGRAM_WEBHOOK_FULL}"
    )
