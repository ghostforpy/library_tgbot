EMPTY = {}
CANCEL = {"cancel":"Отмена"}
CANCEL_SKIP = {"cancel":"Отмена","skip":"Пропустить"}
SKIP = {"skip":"Пропустить"}
OK = {"ok":"OK"}
START = {"start":"/start"}
FINISH = {"finish":"Завершить"}
YES_NO = {
    "RU": {"yes":"Да", "no":"Нет"},
    "UZ": {"yes":"Ha", "no":"Yo'q"},
    "EN": {"yes":"Yes", "no":"No"},
}
CHANGE_SKIP = {"change":"Изменить", "skip":"Пропустить"}
BACK = {"back":"Вернуться в основное меню"} 
FIND = {
    "RU":{"find_members":{"label":"Найти однокурсника","type":"switch_inline"}},
    "UZ":{"find_members":{"label":"Kursdoshni qidirish","type":"switch_inline"}},
    "EN":{"find_members":{"label":"Find a classmate","type":"switch_inline"}},
}
HOME = {
    "RU":{"start":"Домой"},
    "UZ":{"start":"Bosh sahifa"},
    "EN":{"start":"Home"},
}
def make_manage_usr_btn(user_id, show_full_profile=False, lang="RU"):
    msg = {
        "RU": "Получить контакт",
        "UZ": "Kontaktni oling",
        "EN": "Get contact",
    }
    manage_usr_btn = {
          "direct_communication_"+ str(user_id):msg.get(lang, msg["RU"]),
    }
    if show_full_profile:
        manage_usr_btn["full_profile_"+ str(user_id)] = "Полный профиль"
    return manage_usr_btn

def back_to_user_btn(user_id):
    return {"back_to_user_"+ str(user_id):"Назад"}