from telegram.update import Update

# from telegram import ParseMode
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
)

from tgbot.handlers.main.messages import back_btn

# from telegram.error import BadRequest
from telegram import ChatAction

# from telegram.utils.helpers import escape_markdown
from django.utils.translation import gettext as _

from django.conf import settings

# from sentry_sdk import capture_exception
from django.core.paginator import Paginator

from django.utils.translation import override as translation_override

# from config.constants import StatusCode
# from sheduler.models.messages import MessagesToSend
from tgbot.my_telegram.conversationhandler import (
    MyConversationHandler as ConversationHandler,
)
from django.core.cache import caches
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.main.messages import back
from tgbot.utils import send_message, _get_file_id, get_uniq_file_name
import tgbot.models as mymodels
from books.models import Book, UserBookProgress
from tgbot.handlers.main.handlers import start_contact_us

cache = caches["default"]


# Обработка отправки сообщений
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    command_start(update, context)
    return ConversationHandler.END


def start_user_books_library(update: Update, context: CallbackContext):
    page_num = 1
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        page_num = int(query.data.split("-")[1])
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    books_progresses = (
        user.readed_books.order_by("created_at").select_related("book").all()
    )
    context.user_data["current_page_num_library"] = page_num
    BOOKS_PER_PAGE = 10
    p = Paginator(books_progresses, BOOKS_PER_PAGE)
    page = p.page(page_num)
    header_buttons = dict()
    if page.has_previous():
        header_buttons[f"user_books_library-{page.previous_page_number()}"] = "⬅️"
    with translation_override(user.language):
        header_buttons[f"new_book-{page_num}"] = _("Новая")
        if page.has_next():
            header_buttons[f"user_books_library-{page.next_page_number()}"] = "➡"
        btns = {}
        if page:
            text = _("Выберите книгу или загрузите новую") + "\n\n"
            for idx, book_p in enumerate(page, start=1):
                text += f"<b>{(page_num-1)* BOOKS_PER_PAGE +idx}.</b> {book_p.book} - {book_p.progress}\n\n"
                if book_p.book.book_type == "txt":
                    btns[f"page-{book_p.book_id}-{book_p.progress_txt}"] = str(
                        (page_num - 1) * BOOKS_PER_PAGE + idx
                    )
        else:
            text = _("В вашей библиотеке пока нет книг. Загрузите чтобы начать чтение")
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            btns, "inline", 5, header_buttons=header_buttons, footer_buttons=back()
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "working-user-books"


def blank(update: Update, context: CallbackContext):
    pass


def render_wait_book_title(update, user, page_num):
    with translation_override(user.language):
        text = _("Введите название книги")
        kwargs = {
            "text": text,
            "reply_markup": make_keyboard(
                {},
                "inline",
                1,
                footer_buttons={f"user_books_library-{page_num}": back_btn()},
            ),
        }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user.user_id, **kwargs)
    return "upload_book"


def add_new_book(update: Update, context: CallbackContext):
    context.user_data.pop("new_book", None)
    if update.message:
        user_id = update.message.from_user.id
        page_num = context.user_data["current_page_num_library"]
    else:
        query = update.callback_query
        user_id = query.from_user.id
        page_num = query.data.split("-")[1]
        context.user_data["current_page_num_library"] = page_num
        query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    return render_wait_book_title(update, user, page_num)


def render_wait_book_file(update, context, user_lang, user_id):
    with translation_override(user_lang):
        text = _("Пришлите файл книги. Поддерживается txt или fb2.")
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            {},
            "inline",
            1,
            footer_buttons={
                f'new_book-{context.user_data["current_page_num_library"]}': back_btn()
            },
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "upload_book"


def handle_new_book_title(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    if len(update.message.text) > 150:
        with translation_override(user.language):
            send_message(
                user_id, text=_("Наименование книги должно быть не более 150 знаков")
            )
            return add_new_book(update, context)
    context.user_data["new_book"] = {"title": update.message.text}
    return render_wait_book_file(update, context, user.language, user_id)


def manage_book_file_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    file_id, filename_orig = _get_file_id(update.message)
    filename_orig = str(user.user_id) + "-" + filename_orig
    filename_lst = filename_orig.split(".")
    if filename_lst[1].lower() not in ["txt", "fb2"]:
        with translation_override(user.language):
            send_message(
                update.message.from_user.id, text=_("Формат не поддерживается")
            )
            return render_wait_book_file(
                update, context, user.language, update.message.from_user.id
            )

    newFile = context.bot.get_file(file_id)
    filename = get_uniq_file_name(
        f"{settings.MEDIA_ROOT}/books_files", filename_lst[0], filename_lst[1]
    )
    newFile.download(f"{settings.MEDIA_ROOT}/books_files/{filename}")
    if "new_book" not in context.user_data:
        with translation_override(user.language):
            return render_wait_book_title(
                update, user, context.user_data["current_page_num_library"]
            )
    if "title" not in context.user_data["new_book"]:
        with translation_override(user.language):
            send_message(update.message.from_user.id, text=_("Введите название книги"))
            return render_wait_book_title(
                update, user, context.user_data["current_page_num_library"]
            )

    book = Book.objects.create(
        title=context.user_data["new_book"]["title"],
        user_upload=user,
        file=f"books_files/{filename}",
        file_id=file_id,
        book_type=filename_lst[1].lower(),
    )
    ubp = UserBookProgress.objects.create(book=book, user=user)
    try:
        if book.book_type == "txt":
            ubp.total_pages_txt_book = len(book.get_paginated_book_txt())
        else:
            book.read_fb2_book()
            ubp.total_sections_fb_book = len(book.get_chapters_fb2_book())
            # ubp.total_pages_txt_book = len(book.get_paginated_book_txt())
    except Exception as e:
        with translation_override(user.language):
            send_message(
                update.message.from_user.id,
                text=_("При чтении книги произошла ошибка"),
            )
        ubp.delete()
        book.delete()
        return render_wait_book_file(
            update, context, user.language, update.message.from_user.id
        )
    del context.user_data["new_book"]
    with translation_override(user.language):
        text = _("Книга удачно загружена")
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            {},
            "inline",
            1,
            footer_buttons={f"user_books_library-1": back_btn()},
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(update.message.from_user.id, **kwargs)
    return "working-user-books"


def change_book_page(update: Update, context: CallbackContext):
    page_num = 1
    if update.message:
        user_id = update.message.from_user.id
        book_id = int(context.user_data["current_book"])
        page_num = int(update.message.text)
    else:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        book_id = int(query.data.split("-")[1])
        context.user_data["current_book"] = book_id
        page_num = int(query.data.split("-")[2])
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    ubp = (
        UserBookProgress.objects.filter(user_id=user_id, book_id=book_id)
        .select_related("book")
        .first()
    )
    if ubp.book.book_type == "txt":
        ubp.progress_txt = int(page_num)
        p = Paginator(ubp.book.get_paginated_book_txt(), 1)
    ubp.save()
    if page_num > p.num_pages:
        page_num = p.num_pages
    if page_num == 0:
        page_num = 1
    page = p.page(page_num)
    header_buttons = dict()
    if page.has_previous():
        header_buttons[f"page-{ubp.book_id}-{page.previous_page_number()}"] = "⬅️"
    # if page_num not in [1, 2]:
    #     header_buttons[f"page-{ubp.book_id}-1"] = "⏹️"
    if page.has_next():
        header_buttons[f"page-{ubp.book_id}-{page.next_page_number()}"] = "➡"
    with translation_override(user.language):
        btns = {}
        if page:
            text = (
                _("Страница") + f" {page_num} " + _("из") + f" {p.num_pages}" + "\n\n"
            )
            text += page[0]
            btns = {f"wait_page-{book_id}-{page_num}": _("Перейти")}
        else:
            text = _("Проблемы с отображением книги")
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            btns,
            "inline",
            1,
            header_buttons=header_buttons,
            footer_buttons={
                f'user_books_library-{context.user_data["current_page_num_library"]}': back_btn()
            },
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "working-book"


def handle_wait_page(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    query.answer()
    current_book_id = int(query.data.split("-")[1])
    page_num = int(query.data.split("-")[2])
    context.user_data["current_book"] = current_book_id
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    with translation_override(user.language):
        text = _("Введите номер нужной страницы")
    kwargs = {
        "text": text,
        "reply_markup": make_keyboard(
            {},
            "inline",
            1,
            footer_buttons={f"page-{current_book_id}-{page_num}": back_btn()},
        ),
    }
    if update.callback_query:
        update.callback_query.edit_message_text(**kwargs)
    else:
        send_message(user_id, **kwargs)
    return "working-book"


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    messages_conv = ConversationHandler(  # здесь строится логика разговора
        persistent=True,
        name="user_books_conversation",
        conversation_timeout=60 * 60 * 12,  # 12 hours
        # точка входа в разговор
        entry_points=[
            CallbackQueryHandler(
                start_user_books_library, pattern="^user_books_library-1$"
            ),
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working-user-books": [
                CallbackQueryHandler(
                    start_user_books_library, pattern="^user_books_library-\d+$"
                ),
                CallbackQueryHandler(add_new_book, pattern="^new_book-\d+$"),
                CallbackQueryHandler(change_book_page, pattern="^page-\d+-\d+$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, blank),
            ],
            "upload_book": [
                CallbackQueryHandler(
                    start_user_books_library, pattern="^user_books_library-\d+$"
                ),
                CallbackQueryHandler(add_new_book, pattern="^new_book-\d+$"),
                MessageHandler(
                    Filters.text & FilterPrivateNoCommand, handle_new_book_title
                ),
                MessageHandler(
                    Filters.document & FilterPrivateNoCommand, manage_book_file_action
                ),
            ],
            "working-book": [
                CallbackQueryHandler(
                    start_user_books_library, pattern="^user_books_library-\d+$"
                ),
                CallbackQueryHandler(handle_wait_page, pattern="^wait_page-\d+-\d+$"),
                CallbackQueryHandler(change_book_page, pattern="^page-\d+-\d+$"),
                MessageHandler(
                    Filters.regex(r"^\d+$") & FilterPrivateNoCommand, change_book_page
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
    dp.add_handler(messages_conv)
