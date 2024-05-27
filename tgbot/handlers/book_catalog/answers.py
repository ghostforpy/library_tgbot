from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override

choose_book_msg = lambda: _("Выбрана книга")


def choose_book_msgs():
    r = {"RU": "Выбрана книга"}
    with translation_override("UZ"):
        r.update({"EN": _("Выбрана книга")})
    return r


CHOOSE_BOOK_MSG = choose_book_msgs()
find_book = lambda: {"find_book": {"label": _("Найти книгу"), "type": "switch_inline"}}
