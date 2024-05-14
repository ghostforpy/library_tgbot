from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override
from telegram.update import Update
# from telegram import ReplyKeyboardRemove
from telegram.ext.callbackcontext import CallbackContext
from telegram.error import BadRequest

from tgbot.models import NewUser
from tgbot.handlers.keyboard import make_keyboard
from tgbot import utils
from tgbot.models.status import Status
from tgbot.utils import send_message

from .messages import *
from .answers import *

def prepare_ask_language(update: Update, context: CallbackContext, new_user: NewUser):
    languages = {
        item[0]: item[1] for item in NewUser.LANGUAGE
    }
    kwargs = {
        "text": ASK_LANGUAGE[new_user.language],
        "reply_markup": make_keyboard(languages,"inline",1)
    }
    if update.message is not None:
        send_message(
                user_id=update.message.from_user.id,
                **kwargs
            )
    elif update.callback_query is not None:
        try:
            update.callback_query.edit_message_text(
                **kwargs
            )
        except BadRequest:
            send_message(
                user_id=update.callback_query.from_user.id,
                **kwargs
            )


def prepare_ask_phone(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
    with translation_override(new_user.language):
        kwargs = {
            "text": aks_phone(),
            "reply_markup": make_keyboard(
                {},"usual",2,request_phone(),step_back()
            )
        }
    if update.message is not None or new_message:
        send_message(
            user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
            **kwargs
        )
    elif update.callback_query is not None:
        try:
            update.callback_query.edit_message_text(
                **kwargs
            )
        except BadRequest:
            send_message(
                user_id=update.callback_query.from_user.id,
                **kwargs
            )


def prepare_ask_photo(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
    with translation_override(new_user.language):
        kwargs = {
            "text": ask_photo(),
            "reply_markup": make_keyboard({},"inline",2,skip_btn(),step_back())
        }
    if update.message is not None or new_message:
        send_message(
            user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
            **kwargs
        )
    elif update.callback_query is not None:
        try:
            update.callback_query.edit_message_text(
                **kwargs
            )
        except BadRequest:
            send_message(
                user_id=update.callback_query.from_user.id,
                **kwargs
            )


def prepare_ask_first_name(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
    with translation_override(new_user.language):
        kwargs = {
            "text": ask_firstname(),
            "reply_markup": make_keyboard({},"usual",2)
        }
    if update.message is not None or new_message:
        send_message(
            user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
            **kwargs
        )
    elif update.callback_query:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
        )


def prepare_ask_patronymic(update: Update, context: CallbackContext, new_user: NewUser):
    kwargs = {
        "text": ASK_PATRONYMIC[new_user.language],
        "reply_markup": make_keyboard({},"usual",2)
    }
    if update.message is not None:
        update.message.reply_text(
            **kwargs
        )
    elif update.callback_query is not None:
        try:
            update.callback_query.edit_message_text(
                **kwargs
            )
        except BadRequest:
            send_message(
                user_id=update.callback_query.from_user.id,
                **kwargs
            )


def prepare_ask_lastname(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
    with translation_override(new_user.language):
        kwargs = {
            "text": ask_lastname(),
            "reply_markup": make_keyboard(step_back(),"inline",2)
        }
    if update.message is not None or new_message:
        send_message(
            user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
            **kwargs
        )
    elif update.callback_query:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
        )


def prepare_ask_role(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
    role_btns = dict()
    for role in Status.objects.filter(view_in_tgbot=True):
        role_btns[role.id] = role.name
        f_role = role.statusforeingname_set.filter(language=new_user.language).first()
        if new_user.language != role.language and f_role:
            role_btns[role.id] = f_role.translate
    with translation_override(new_user.language):
        kwargs = {
            "text": ask_role(),
            "reply_markup": make_keyboard(
                role_btns,
                "inline",
                1,
                footer_buttons=step_back()
            )
        }
    if update.message is not None or new_message:
        send_message(
            user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
            **kwargs
        )
    elif update.callback_query:
        send_message(
            user_id=update.callback_query.from_user.id,
            **kwargs
        )


# def prepare_ask_shop(update: Update, context: CallbackContext, new_user: NewUser, new_message=False):
#     with translation_override(new_user.language):
#         footer_buttons = skip_btn()
#         footer_buttons.update(step_back())
#         kwargs = {
#             "text": find_shop_message(),
#             "reply_markup": make_keyboard(
#                 find_shop(),
#                 "inline",
#                 1,
#                 footer_buttons=footer_buttons
#             )
#         }
#     if update.message is not None or new_message:
#         send_message(
#             user_id=update.message.from_user.id if update.message else update.callback_query.from_user.id,
#             **kwargs
#         )
#     elif update.callback_query:
#             update.callback_query.edit_message_text(
#                     **kwargs
#                 )



def prepare_ask_about(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    update.message.reply_text(ASK_ABOUT + f"\n Уже введено: '{utils.mystr(new_user.about)}'", reply_markup=keyboard)


def prepare_ask_birthday(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    birthday = utils.mystr(new_user.date_of_birth)
    update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{birthday}'", reply_markup=keyboard)


def prepare_ask_email(update: Update, context: CallbackContext, new_user: NewUser):
    keyboard = make_keyboard(CANCEL,"usual",2)
    update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)



