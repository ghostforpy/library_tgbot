from django.utils.translation import gettext as _

REGISTRATION_CANCELED = {
    "RU": "Регистрация отменена.",
    "EN": "Registration cancelled.",
    "UZ": "Ro'yxatdan o'tish bekor qilindi.",
}
registration_canceled = lambda: _("Регистрация отменена.")
ASK_REENTER = "Пожалуйста, просто нажми кнопку «Отправить номер», "\
    "ничего не вводя в поле. Номер отправится автоматически. "\
        "Если кнопка не видна, откройте меню, как указано на картинке выше."  

USERNAME_NEEDED = "<b>Рекомендуется создать имя пользователя в настройках своего профиля Telegram.</b>"

registration_start_mess = lambda name: _('Здравствуйте') + f", {name}" + _('добро пожаловать в "Library TGbot"!')

WELCOME_REG = {
    "RU": "Вас приветствует Bot - "\
    "интерактивный помощник сообщества.",
    "EN": "EN Вас приветствует Bot - "\
    "интерактивный помощник сообщества.",
    "UZ": "UZ Вас приветствует Bot - "\
    "интерактивный помощник сообщества.",
}

ASK_PHONE = {
    "RU": "Отправьте контакт или введите номер в формате +998991112233",
    "UZ": "Kontaktni yuboring yoki raqamni +998991112233 formatida kiriting",
    # "EN": "Send a contact or enter a number in the format +998991112233"
}
aks_phone = lambda: _("Отправьте контакт или введите номер в формате +998991112233")
ASK_FIO = "Ваше ФИО взяты из Телеграм '{}'. Можете ввести другие или пропустить этот шаг."

ASK_LANGUAGE = {
    "RU": "Выберите язык",
    # "EN": "Select a language",
    "UZ": "Tilni tanlang"
}

ASK_FIRSTNAME = {
    "RU": "Имя",
    "UZ": "Ismingiz",
    # "EN": "Name"
}
ask_firstname = lambda: _("Имя")
ASK_LASTNAME = {
    "RU": "Фамилия",
    "UZ": "Familiyangiz",
    # "EN": "Lastname"
}
ask_lastname = lambda: _("Фамилия")
ASK_ROLE = {
    "RU": "Роль",
    "UZ": "Roli",
}
ask_role = lambda: _("Роль")
FIND_SHOP_MESSAGE = {
    "RU":   "Нажмите кнопку поиска и введите на выбор: наименование магазина, регион, телефон.",
    "UZ":   "Qidiruv tugmachasini bosing va tanlang: do'kon nomi, mintaqa, telefon.",
}
find_shop_message = lambda: _("Нажмите кнопку поиска и введите на выбор: наименование магазина, регион, телефон.")
ASK_PATRONYMIC = {
    "RU": "Отчество"
}

ASK_ABOUT = "Напишите подробно о своей деятельности: в каких компаниях работаете/работали или основали? " \
            "Над какими проектами сейчас работаете? Ваши достижения."

ASK_BIRHDAY = "Сообщите Ваш день рождения в формате дд.мм.гггг."

BAD_DATE = "Дата введена неверно. Повторите ввод в формате дд.мм.гггг"

ASK_EMAIL = "Укажите ваш E-mail в формате <b>example@domain.ru</b>. " \
            "E-mail необходим для рассылки новостей, важных изменений, наград за участие и т.д."
           
BAD_EMAIL = "E-mail введен неверно. Пожалуйста повторите ввод"

# ASK_CITY = {
#     "RU": "Где проживаете?",
#     "UZ": "Qayerda yashaysiz?",
#     "EN": "Where do you live?",
# }

ASK_SHOP = {
    "RU": "Название бренда",
    "UZ": "Brend nomi",
    "EN": "Brand name",
}

# ASK_JOB = {
#     "RU": "Выберите должность",
#     "UZ": "Lavozimingiz",
#     "EN": "Choose a position",
# }


ASK_JOB_REGION = "8. Регионы присутствия вашего бизнеса"

ASK_SITE = "7. Адрес сайта"

BAD_SITE = "Укажите пожалуйста сайт именно ссылкой"

CHECK_ICON = "☑️ "

ASK_PHOTO = {
    "RU":'Загрузите свою фотографию или нажмите "Пропустить"',
    "EN":'Upload your photo or click "Skip"',
    "UZ":'''Suratingizni yuklang yoki "o'tkazib yuborish" tugmasini bosing''',
}
ask_photo = lambda: _('Загрузите свою фотографию или нажмите "Пропустить"')

