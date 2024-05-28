from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    InlineQueryHandler,
    ChosenInlineResultHandler,
    Filters,
)
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.parsemode import ParseMode
from django.utils.translation import gettext as _
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils.translation import override as translation_override
from django.core.cache import caches
from tgbot.my_telegram.conversationhandler import (
    MyConversationHandler as ConversationHandler,
)
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.main.messages import back, back_btn
from tgbot.utils import send_message
import tgbot.models as mymodels
from books.models import Book, UserBookProgress
from tgbot.handlers.main.handlers import start_contact_us

from .answers import *

cache = caches["default"]


# Обработка отправки сообщений
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END


def start_book_catalog(update: Update, context: CallbackContext):
    page_num = 1
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        page_num = int(query.data.split("-")[1])
    user = mymodels.User.get_user_by_username_or_user_id(user_id)

    books_progresses = UserBookProgress.objects.filter(user_id=user_id).values_list(
        "book_id", flat=True
    )
    books = (
        Book.objects.exclude(id__in=books_progresses)
        .filter(moderator_approved=True)
        .order_by("author", "title")
        .all()
    )
    context.user_data["current_page_num_book_catalog"] = page_num
    BOOKS_PER_PAGE = 10
    p = Paginator(books, BOOKS_PER_PAGE)
    page = p.page(page_num)
    header_buttons = dict()
    if page.has_previous():
        header_buttons[f"book_catalog-{page.previous_page_number()}"] = "⬅️"
    with translation_override(user.language):
        if page.has_next():
            header_buttons[f"book_catalog-{page.next_page_number()}"] = "➡"
        btns = {}
        if page:
            text = _("Выберите книгу") + "\n\n"
            for idx, book in enumerate(page, start=1):
                text += f"<b>{(page_num-1)* BOOKS_PER_PAGE +idx}.</b> {book}\n\n"
                btns[f"book-{book.id}-{page_num}"] = str(
                    (page_num - 1) * BOOKS_PER_PAGE + idx
                )

        else:
            text = _("На этой странице каталога пока что пусто")
    footer_buttons = find_book().copy()
    footer_buttons.update(back())
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            btns,
            "inline",
            5,
            header_buttons=header_buttons,
            footer_buttons=footer_buttons,
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs, parse_mode=ParseMode.HTML)
    else:
        send_message(user_id, **kwargs)
    return "working-book-catalog"


def blank(update: Update, context: CallbackContext):
    pass


def add_book_to_user_library(update: Update, context: CallbackContext):
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        page_num = int(query.data.split("-")[-1])
        book_id = int(query.data.split("-")[1])
    elif update.chosen_inline_result:
        user_id = update.chosen_inline_result.from_user.id
        book_id = int(update.chosen_inline_result.result_id)
        page_num = context.user_data["current_page_num_book_catalog"]
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    book = Book.objects.filter(id=book_id).first()
    with translation_override(user.language):
        if book:
            ubp = UserBookProgress(book_id=book_id, user_id=user_id)
            if book.book_type == "txt":
                ubp.total_pages_txt_book = len(book.get_paginated_book_txt())
            else:
                book.read_fb2_book()
                ubp.total_sections_fb_book = len(book.get_chapters_fb2_book())
                ubp.total_pages_txt_book = len(book.get_paginated_chapter_book_fb2(1))
            ubp.save()
            text = _("Книга успешно добавлена в Вашу библиотеку")
        else:
            text = _("К сожалению что-то пошло не так")

    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            {}, "inline", 5, footer_buttons={f"book_catalog-{page_num}": back_btn()}
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs, parse_mode=ParseMode.HTML)
    else:
        send_message(user_id, **kwargs)
    return "working-book-catalog"


# Обработчик поиска
def manage_find_book(update: Update, context: CallbackContext):
    user_id = update.inline_query.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    query = update.inline_query.query.strip()

    books_progresses = UserBookProgress.objects.filter(user_id=user_id).values_list(
        "book_id", flat=True
    )
    books_set = (
        Book.objects.exclude(id__in=books_progresses)
        .filter(
            Q(moderator_approved=True)
            & (Q(title__icontains=query) | Q(author__icontains=query))
        )
        .order_by("author", "title")
        .all()
        .distinct()
    )

    results = []
    with translation_override(user.language):
        msg = choose_book_msg()
    for _book in books_set:
        _u = InlineQueryResultArticle(
            id=f"{_book.id}",
            title=str(_book),
            input_message_content=InputTextMessageContent(msg),
        )
        # if not settings.DEBUG:
        #     thumb_url = f"{settings.DOMAIN}/media/no_foto.jpg"
        #     if user.main_photo != "":
        #         thumb_url = f"{settings.DOMAIN}{_user.main_photo.url}"
        #     _u.thumb_url = thumb_url
        #     _u.thumb_width = 25
        #     _u.thumb_height = 25
        results.append(_u)
    update.inline_query.answer(results, cache_time=5, auto_pagination=True)


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    book_catalog_conv = ConversationHandler(  # здесь строится логика разговора
        persistent=True,
        name="book_catalog_conversation",
        conversation_timeout=60 * 60 * 12,  # 12 hours
        # точка входа в разговор
        entry_points=[
            CallbackQueryHandler(start_book_catalog, pattern="^book_catalog-1$"),
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working-book-catalog": [
                InlineQueryHandler(manage_find_book),
                ChosenInlineResultHandler(add_book_to_user_library),
                MessageHandler(
                    Filters.regex(
                        "|".join([f"^{CHOOSE_BOOK_MSG[i]}$" for i in CHOOSE_BOOK_MSG])
                    )
                    & FilterPrivateNoCommand,
                    blank,
                ),
                CallbackQueryHandler(start_book_catalog, pattern="^book_catalog-\d+$"),
                CallbackQueryHandler(
                    add_book_to_user_library, pattern="^book-\d+-\d+$"
                ),
                MessageHandler(Filters.text & FilterPrivateNoCommand, blank),
            ],
        },
        # точка выхода из разговора
        fallbacks=[
            CallbackQueryHandler(stop_conversation, pattern="^start$"),
            CommandHandler("cancel", stop_conversation, Filters.chat_type.private),
            CommandHandler("start", stop_conversation, Filters.chat_type.private),
            CommandHandler("help", start_contact_us, Filters.chat_type.private),
        ],
    )
    dp.add_handler(book_catalog_conv)
