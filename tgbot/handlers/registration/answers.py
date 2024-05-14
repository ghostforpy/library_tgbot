from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override
from tgbot.handlers.main.messages import back_btn

EMPTY = {}
BACK = {"back":"Вернуться в основное меню"} 
CANCEL = {"cancel":"Прервать регистрацию"}
CANCEL_CREATE = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Прервать регистрацию","skip":"Пропустить"}
SKIP = {
    "RU": {"skip":"Пропустить"},
    "UZ": {"skip":"O'tkazib yuborish"},
    # "EN": {"skip":"Skip"},
}
skip_btn = lambda: {"skip": _("Пропустить")}
OK = {"ok":"OK"}
START = {"start":"/start"}
APPROVAL_ANSWERS = {"yes":"Согласен", "no":"Пропустить"}
YES_NO = {
    "RU": {"yes_completion_of_training":"Да", "no_completion_of_training":"Нет"},
    "UZ": {"yes_completion_of_training":"Ha", "no_completion_of_training":"Yo'q"},
    # "EN": {"yes_completion_of_training":"Yes", "no_completion_of_training":"No"},
}
NO = {"no":"Нет"}
YES_NO_CANCEL = YES_NO | CANCEL
registration_start_btn = lambda: {"reg_start": _("Регистрация")}
REQUEST_PHONE = {
    "RU": {"reg_start":{"label":"Отправить контакт","type":"phone"}},
    "UZ": {"reg_start":{"label":"Kontaktni yuboring","type":"phone"}},
    # "EN": {"reg_start":{"label":"Send contact","type":"phone"}}
}
request_phone = lambda: {"reg_start": {"label": _("Отправить контакт"), "type":"phone"}}
CANCEL_SKIP_REQUEST_PHONE = {"reg_start":{"label":"Отправить телефонный номер","type":"phone"},
                             "cancel":"Прервать регистрацию"}
NEXT = {"next": "💾 Готово"}
CREATE = {"create": "Другое"}

FIND_MEMB = {
    "find_members_registration":
        {"label":"Найти пользователя","type":"switch_inline"},
    "skip": "Пропустить"
    }

FIND_SHOP = {
    "RU":{"find_shops":{"label":"Найти магазин","type":"switch_inline"}},
    "UZ":{"find_shops":{"label":"Do'konni toping","type":"switch_inline"}},
}
find_shop = lambda: {"find_shops": {"label": _("Найти магазин"), "type": "switch_inline"}}
INPUT_NEXT_MSG_CONTENT_CHOSEN_MEMBER = "Выбран пользователь"
INPUT_NEXT_MSG_CONTENT_CHOSEN_SHOP = {
    "RU": "Выбран магазин",
    "UZ": "Do'kon tanlandi",
}

choose_shop_msg = lambda: _("Выбран магазин")

def choose_shop_msgs():
    r = {"RU": "Выбран магазин"}
    with translation_override("UZ"):
        r.update(
            {"UZ": _("Выбран магазин")}
        )
    return r

CHOOSE_SHOP_MSG = choose_shop_msgs()


BAD_PHOTO = {
    "RU": "Пришлите именно фотографию",
    # "EN": "Send exactly the photo",
    "UZ": "Fotosuratni yuboring",
}
bad_photo = lambda: _("Пришлите именно фотографию")

STEP_BACK = {
    "RU": {"back": back_btn()},
}
with translation_override("UZ"):
    STEP_BACK.update(
        {"UZ": {"back": back_btn()}}
    )
step_back = lambda: {"back": back_btn()}
STEP_BACK_OTHER = {
    "RU": {"back_other": "⬅️ Назад"},
    "UZ": {"back_other": "⬅️ Orqaga"},
    # "EN": {"back_other": "⬅️ Back"},
}