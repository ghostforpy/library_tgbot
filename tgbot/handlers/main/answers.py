from config.constants import StatusCode
from tgbot.models import User
from tgbot.handlers.keyboard import make_keyboard
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override

EMPTY = {}
CANCEL = {"cancel": "Отмена"}
CANCEL_SKIP = {"cancel": "Отмена", "skip": "Пропустить"}
OK = {"ok": "OK"}
START = {"start": "/start"}
YES_NO = {"yes": "Да", "no": "Нет"}


TO_ADMINS = {"to_admins": "Сообщение администраторам"}


full_menu = lambda: {
    "library": _("Библиотека"),
}

start_menu_short = lambda: {
    # "profile":"🖊 " + _("Мой профиль"),
    "contact_us": _("Связаться с нами")
}


start_menu_admin = lambda: {
    "library": _("Библиотека"),
}


def get_start_menu(user: User):
    with translation_override(user.language):
        if user.is_banned:
            return make_keyboard(TO_ADMINS, "inline", 1)
        elif user.is_blocked_bot or not user.verified_by_admin:
            return make_keyboard(start_menu_short(), "inline", 1)
        elif user.is_admin:
            return make_keyboard(
                start_menu_admin(), "inline", 1, footer_buttons=start_menu_short()
            )
        else:
            return make_keyboard(
                start_menu_short(), "inline", 1, footer_buttons=start_menu_short()
            )
