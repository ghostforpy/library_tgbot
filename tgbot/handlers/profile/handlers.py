import os
# import urllib.parse as urllibparse

import telegram
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, 
    # CommandHandler,
    # MessageHandler, 
    CallbackQueryHandler,
    # Filters,
    ConversationHandler,
)
# from telegram import InputMediaDocument, MessageEntity
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings

# from dtb.constants import StatusCode
from tgbot.handlers.main.messages import back_btn

import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
# from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.handlers.commands import command_start
from tgbot.handlers.utils import send_photo, fill_file_id, get_no_foto_id, wrong_file_id
from tgbot.utils import mystr, is_date, is_email, get_uniq_file_name, _get_file_id, send_message

from .messages import *
from .answers import *
from .prepares import (
    prepare_manage_personal_info,
    prepare_manage_busines_info,
    # prepare_company_business_branches,
    prepare_go_start_conversation,
    # prepare_company_business_needs,
    # prepare_company_business_benefits
)
# Возврат к главному меню в исключительных ситуациях
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    update.message.reply_text(PROF_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    command_start(update, context)
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(EMPTY,"usual",2))

# Начало работы с профилем
def start_conversation(update: Update, context: CallbackContext):

    query = update.callback_query
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query.answer()
    query.edit_message_text(text=PROF_HELLO)

    if not(user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        if not user.main_photo_id:
            fill_file_id(user, "main_photo")
        photo = user.main_photo.path
        photo_id = user.main_photo_id
    
    profile_txt = user.full_profile()
    reply_markup = make_keyboard_start_menu()

    if os.path.exists(photo):
        # send_photo(user.user_id, photo_id)
        send_photo(user.user_id, photo_id, caption=profile_txt, reply_markup=reply_markup)
    else:
        send_message(user_id = user.user_id,text = NOT_FOTO)
        send_message(user_id = user.user_id, text = profile_txt, reply_markup = reply_markup, 
                     disable_web_page_preview=True)

    return "working"

def go_start_conversation(update: Update, context: CallbackContext):
    prepare_go_start_conversation(update, context)
    # reply_markup = make_keyboard_start_menu()
    # update.message.reply_text(PROF_HELLO, reply_markup = reply_markup)
    return "working"

# Начало работы с персональной инфо
def manage_personal_info(update: Update, context: CallbackContext):
    prepare_manage_personal_info(update, context)
    # reply_markup = make_keyboard_pers_menu()
    # update.message.reply_text(PERSONAL_START_MESSS, reply_markup = reply_markup)
    return "working_personal_info"

# Начало работы с бизнес инфо
def manage_busines_info(update: Update, context: CallbackContext):
    prepare_manage_busines_info(update, context)
    # reply_markup = make_keyboard_busines_menu()
    # update.message.reply_text(BUSINES_START_MESSS, reply_markup = reply_markup)
    return "working_busines_info"

# Начало работы с инфо о себе
def manage_about_info(update: Update, context: CallbackContext):
    reply_markup = make_keyboard_about_menu()
    update.message.reply_text(ABOUT_START_MESSS, reply_markup = reply_markup)
    return "working_about_info"

#------------------------------------------- 
# Обработчики персональной инфы
#------------------------------------------- 
# Обработчик имени
def manage_first_name(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    first_name = mystr(user.first_name)
    update.message.reply_text(
        ASK_FIRST_NAME.format(first_name), 
        reply_markup=make_keyboard(SKIP,"usual",1)
    )
    return "choose_action_first_name"

def manage_first_name_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.first_name = update.message.text
        user.save()
        text = "Имя изменено"
    else:
        text = "Имя не изменено"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

# Обработчик отчества
def manage_patronymic(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    patronymic = mystr(user.patronymic)
    update.message.reply_text(
        ASK_PATRONYMIC.format(patronymic),
        reply_markup=make_keyboard(SKIP,"usual",1)
    )
    return "choose_action_patronymic"

def manage_patronymic_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.patronymic = update.message.text
        user.save()
        text = "Отчество изменено"
    else:
        text = "Отчество не изменено"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

# Обработчик фамилии
def manage_last_name(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    last_name = mystr(user.last_name)
    update.message.reply_text(
        ASK_FIO.format(last_name),
        reply_markup=make_keyboard(SKIP,"usual",1)
    )
    return "choose_action_last_name"

def manage_last_name_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.last_name = update.message.text
        user.save()
        text = "Фамилия изменена"
    else:
        text = "Фамилия не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

def manage_fio_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        # user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        fio = update.message.text.split()
        len_fio = len(fio)
        if len_fio == 1:
            user.last_name = ""  # Фамилия
            user.first_name = fio[0] # Имя
            user.patronymic = ""   # Отчество
        elif len_fio == 2:
            user.first_name = fio[0] # Имя
            user.last_name = fio[1]  # Фамилия
            user.patronymic = ""   # Отчество
        elif len_fio > 2:
            user.last_name = fio[0]  # Фамилия
            user.first_name = fio[1] # Имя
            user.patronymic = fio[2]   # Отчество
        user.save()
        text = "ФИО изменены"
    else:
        text = "ФИО не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"


#-------------------------------------------  
# Обработчик e-mail
def manage_email(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_EMAIL.format(user.email), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_email"

def manage_email_action(update: Update, context: CallbackContext):
    email = is_email(update.message.text)
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "E-mail не изменен"
    elif not(email): # ввели неверную email
        update.message.reply_text(BAD_EMAIL, make_keyboard(SKIP,"usual",1))
        return 
    else:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.email = email
        user.save()
        text = "E-mail изменен"
        
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

#-------------------------------------------  
# Обработчик телефона
def manage_phone(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_PHONE.format(user.telefon), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_phone"

def manage_phone_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.telefon = update.message.text
        user.save()
        text = "Телефон изменен"
    else:
        text = "Телефон не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

#-------------------------------------------  
# Обработчик День рождения
def manage_date_of_birth(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    birthday = mystr(user.date_of_birth)
    update.message.reply_text(ASK_BIRHDAY.format(birthday), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_date_of_birth"

def manage_date_of_birth_action(update: Update, context: CallbackContext):
    date = is_date(update.message.text)
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "День рождения не изменен"
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, reply_markup=make_keyboard(SKIP,"usual",1))
        return 
    else:
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.date_of_birth = date
        user.save()
        text = BIRHDAY_CHANGED    
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

#-------------------------------------------  
# Обработчик Фото
def manage_main_photo(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if not(user.main_photo):
        photo = settings.BASE_DIR / 'media/no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        photo = user.main_photo.path
        if not user.main_photo_id or wrong_file_id(user.main_photo_id):
            fill_file_id(user, "main_photo", text = "profile_manage_main_photo")
        photo_id = user.main_photo_id
    if os.path.exists(photo):
        update.message.reply_photo(photo_id, caption = ASK_FOTO, reply_markup=make_keyboard(SKIP,"usual",1))
    else:
        update.message.reply_text(NOT_FOTO, reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_main_photo"

def manage_main_photo_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    foto_id, filename_orig = _get_file_id(update.message)
    filename_orig = str(user.user_id) + "-" + filename_orig
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(foto_id)
    filename = get_uniq_file_name(settings.BASE_DIR / "media/user_fotos",filename_lst[0],filename_lst[1])
    newFile.download(settings.BASE_DIR / ("media/user_fotos/"+filename))
    user.main_photo = "user_fotos/"+filename
    user.main_photo_id = foto_id
    user.save()
    text = "Фото изменено"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"

def manage_main_photo_txt_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text == SKIP["skip"]:        
        text = "Фото не изменено"
        update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
        return "working_personal_info"
    else:
        text = "Пришлите именно фотографию или пропустите шаг"
        update.message.reply_text(text,reply_markup=make_keyboard(SKIP,"usual",1))
        return "choose_action_main_photo"
#-------------------------------------------  
# Обработчик Статус
def manage_status(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    text = SAY_STATUS.format(user.status)
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"


#-------------------------------------------  
# Обработчики бизнес инфо
#-------------------------------------------  
# Обработчик Компания
def manage_company(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_COMPANY.format(user.company), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_company"

def manage_company_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.company = update.message.text
        user.save()
        text = "Компания изменена"
    else:
        text = "Компания не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"


#-------------------------------------------  
# Обработчик количества сотрудников компании
def manage_employess_number(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    company_number_of_employees = {
        item[0]: item[1] for item in mymodels.User.COMPANY_NUMBER_OF_EMPLOYESS_CHOISES
    }
    company_number_of_employees["skip"] = "Пропустить"
    update.message.reply_text(
        ASK_EMPLOYESS_NUMBER.format(user.get_number_of_employees_display()),
        reply_markup=make_keyboard({},"usual",1)
    )
    send_message(
        update.message.from_user.id,
        ASK_EMPLOYESS_NUMBER_SELECT,
        reply_markup=make_keyboard(company_number_of_employees,"inline",1)
    )
    return "choose_action_employess_number"

def manage_employess_number_action_message(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        return manage_employess_number(update, context)

def manage_employess_number_action_callback_query(update: Update, context: CallbackContext):
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "skip":
        text = "Количество сотрудников компании не изменено"
    else:    
        user = mymodels.User.objects.get(user_id = update.callback_query.from_user.id)
        user.number_of_employees = variant
        user.save()
        text = "Количество сотрудников компании изменено"
    send_message(
        update.callback_query.from_user.id,
        text,
        reply_markup=make_keyboard_busines_menu()
    )
    return "working_busines_info"

#-------------------------------------------  
# Обработчик Должность
def manage_job(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_JOB.format(user.job), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_job"

def manage_job_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.job = update.message.text
        user.save()
        text = "Должность изменена"
    else:
        text = "Должность не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"

#-------------------------------------------  
# Обработчик Отрасли
def manage_branch(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_BRANCH.format(user.branch), reply_markup=make_keyboard(SKIP,"usual",2))
    return "choose_action_branch"

def manage_branch_action(update: Update, context: CallbackContext):
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.branch = update.message.text
        user.save()
        text = "Отрасль изменена"
    else:
        text = "Отрасль  не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"

#-------------------------------------------  
# Обработчик Город
def manage_city(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_CITI.format(user.city), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_city"

def manage_citi_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.city = update.message.text
        user.save()
        text = "Город изменен"
    else:
        text = "Город не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"

#-------------------------------------------  
# Обработчик Региона
def manage_job_region(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_REGION.format(user.job_region), reply_markup=make_keyboard(SKIP,"usual",2))
    return "choose_action_job_region"

def manage_job_region_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.job_region = update.message.text
        user.save()
        text = "Регион  изменен"
    else:
        text = "Регион  не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"
#-------------------------------------------  
# Обработчик Сайт
def manage_site(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_SITE.format(user.site), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_site"

def manage_site_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)

        validate = URLValidator()
        site = update.message.text
        site = site.lower()
        if not site.startswith("https://") and not site.startswith("http://"):
            site = "http://" + site
        try:
            validate(site)
        except ValidationError:
            update.message.reply_text(BAD_SITE, reply_markup=make_keyboard(SKIP,"usual",2))
            return
        user.site = site
        user.save()
        text = "Сайт изменен"
    else:
        text = "Сайт не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"
#-------------------------------------------  
# Обработчик ИНН
def manage_inn(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_INN.format(user.inn), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_inn"

def manage_inn_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.inn = update.message.text[:12]
        user.save()
        text = "ИНН изменен"
    else:
        text = "ИНН не изменен"
    update.message.reply_text(text, reply_markup=make_keyboard_busines_menu())
    return "working_busines_info"


#-------------------------------------------  
# Обработчики информации о себе
#-------------------------------------------  
# Обработчик о себе
def manage_about(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_ABOUT.format(user.about), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_about"

def manage_about_action(update: Update, context: CallbackContext):
    text = ""
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.about = update.message.text
        user.save()
        text = "Информация 'О себе' изменена"
    else:
        text = "Информация 'О себе' не изменена"
    update.message.reply_text(text, reply_markup=make_keyboard_about_menu())
    return "working_about_info"
#-------------------------------------------  
# Обработчик Спорта
def manage_sport(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    update.message.reply_text(ASK_SPORT.format(user.sport), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_sport"

def manage_sport_action(update: Update, context: CallbackContext):
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.sport = update.message.text
        user.save()
        text = "Виды спорта изменены"
    else:
        text = "Виды спорта не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard_about_menu())
    return "working_about_info"  
#-------------------------------------------  
# Обработчик Хобби
def manage_hobby(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    hobby = user.hobby if user.hobby is not None else ""
    update.message.reply_text(ASK_HOBBY.format(hobby), reply_markup=make_keyboard(SKIP,"usual",1))
    return "choose_action_hobby"

def manage_hobby_action(update: Update, context: CallbackContext):
    if update.message.text != SKIP["skip"]:        
        user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
        user.hobby = update.message.text
        user.save()
        text = "Виды хобби изменены"
    else:
        text = "Виды хобби не изменены"
    update.message.reply_text(text, reply_markup=make_keyboard_pers_menu())
    return "working_personal_info"   
#-------------------------------------------  
# Обработчики основного меню профиля        
#-------------------------------------------  

#-------------------------------------------  
# Обработчик Рекомендатели
def manage_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
    update.message.reply_text(ASK_REFERES.format(str(all_referes_txt)), reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2), disable_web_page_preview=True)
    return "choose_action_referes"

def manage_referes_action(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)    
    if update.message.text == ADD_DEL_SKIP["skip"]:        
        text = "Рекомендатели не изменены"
        update.message.reply_text(text, reply_markup=make_keyboard_start_menu())
        return "working"
    elif update.message.text == ADD_DEL_SKIP["del"]:
        update.message.reply_text("Удаление рекомендателей", reply_markup=make_keyboard(EMPTY,"usual",1))
        all_referes = mymodels.get_model_dict(mymodels.UserReferrers,"pk","referrer", user)
        text = "Выберите удаляемого рекомендателя"
        update.message.reply_text(text, reply_markup=make_keyboard(all_referes,"inline",2,None,FINISH))
        return "delete_referes"
    elif update.message.text == ADD_DEL_SKIP["add"]:
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        text = all_referes_txt + "\nДля добавления рекомендателя введите его фамилию"
        update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1))

        return "add_referes"
    else:
        update.message.reply_text(ASK_REENTER, reply_markup=make_keyboard(ADD_DEL_SKIP,"usual",2))


def delete_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Удаление рекомендателей завершено"
        reply_markup=make_keyboard_start_menu() 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        referer = mymodels.UserReferrers.objects.get(pk=int(variant))
        referer.delete()
        all_referes = mymodels.get_model_dict(mymodels.UserReferrers,"pk","referrer", user)
        if len(all_referes) == 0:
            all_referes_txt = "Все рекомендатели удалены"
            query.edit_message_text(text=all_referes_txt)
            text = "Удаление рекомендателей завершено"
            reply_markup=make_keyboard_start_menu() 
            send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
            return "working"
        else:           
            text ="Выберите удаляемого рекомендателя"
            query.edit_message_text(text, reply_markup=make_keyboard(all_referes,"inline",2,None,FINISH))

def add_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.message.from_user.id)
    if update.message.text == FINISH["finish"]:        
        text = "Завершено добавление рекомендателей"
        update.message.reply_text(text, reply_markup=make_keyboard_start_menu())
        return "working"
    else:
        selected_users = mymodels.get_model_dict(mymodels.User,"pk","first_name,last_name", None,{"last_name":update.message.text})
        if len(selected_users) == 0:
            text = "Такие пользователи не найдены. Повторите ввод или завершите добавление"        
            update.message.reply_text(text, reply_markup=make_keyboard(FINISH,"usual",1), disable_web_page_preview=True)
            return "add_referes"
        else:
            update.message.reply_text("Выбор рекомендателя", reply_markup=make_keyboard(EMPTY,"usual",1))
            text = "Выберите рекомендателя"
            update.message.reply_text(text, reply_markup=make_keyboard(selected_users,"inline",1,None,FINISH))
            return "select_referes"

def select_referes(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(update.callback_query.from_user.id)
    query = update.callback_query
    variant = query.data
    query.answer()
    if variant == "finish":
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Добавление рекомендателей завершено"
        reply_markup=make_keyboard_start_menu() 
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "working"
    else:
        referer = mymodels.User.objects.get(pk=int(variant))
        user_referers =mymodels.UserReferrers.objects.filter(referrer = referer, user = user)
        if len(user_referers) == 0:
            user_referer = mymodels.UserReferrers(referrer = referer, user = user)
            user_referer.save()  
        all_referes_txt = mymodels.get_model_text(mymodels.UserReferrers,["NN","referrer"], user)
        query.edit_message_text(text=all_referes_txt)
        text = "Для добавления рекомендателя введите его фамилию"
        reply_markup=make_keyboard(FINISH,"usual",1)
        send_message(user_id=user.user_id, text=text, reply_markup=reply_markup)   
        return "add_referes"

#-------------------------------------------  
# Обработчик просмотр профиля
def view_profile(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id 
    else:
        user_id = update.callback_query.from_user.id
        update.callback_query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    if not(user.main_photo):
        photo = f"{settings.MEDIA_ROOT}/no_foto.jpg"
    else:
        photo = user.main_photo.path

    if not(user.main_photo):
        photo = f"{settings.MEDIA_ROOT}/no_foto.jpg"
        photo_id = get_no_foto_id()
    else:
        if not user.main_photo_id:
            fill_file_id(user, "main_photo")
        photo = user.main_photo.path
        photo_id = user.main_photo_id
    profile_txt = user.full_profile(language=user.language)
    with translation_override(user.language):
        reply_markup = make_keyboard({"start": back_btn()}, "inline", 1)
    if os.path.exists(photo):
        # send_photo(user.user_id, photo_id)
        send_photo(
            user.user_id,
            photo_id,
            caption=profile_txt,
            reply_markup=reply_markup,
            parse_mode = telegram.constants.PARSEMODE_HTML
        )
    else:
        send_message(user_id = user.user_id,text = NOT_FOTO)
        update.message.reply_text(
            profile_txt, 
            reply_markup = reply_markup, 
            parse_mode = telegram.constants.PARSEMODE_HTML,
            disable_web_page_preview=True
            )
    # return "working"

def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    # conv_handler = ConversationHandler( 
    #     # точка входа в разговор
    #     entry_points=[CallbackQueryHandler(start_conversation, pattern="^profile$")],      
    #     # этапы разговора, каждый со своим списком обработчиков сообщений
    #     states={
    #         "working":[
    #                    MessageHandler(Filters.text([START_MENU["personal_info"]]) & FilterPrivateNoCommand, manage_personal_info),
    #                    MessageHandler(Filters.text([START_MENU["busines_info"]]) & FilterPrivateNoCommand, manage_busines_info),
    #                    MessageHandler(Filters.text([START_MENU["about_info"]]) & FilterPrivateNoCommand, manage_about_info),
                    #    MessageHandler(Filters.text([START_MENU["view_profile"]]) & FilterPrivateNoCommand, view_profile),
    #                 #    MessageHandler(Filters.text([START_MENU["view_profile"]]) & FilterPrivateNoCommand, view_profile),
    #                    MessageHandler(Filters.text(BACK["back"]) & FilterPrivateNoCommand, stop_conversation),
    #                    MessageHandler(Filters.text & FilterPrivateNoCommand, blank),

    #                   ],
            
    #         "working_personal_info":[
    #                 MessageHandler(Filters.text([PERSONAL_MENU["first_name"]]) & FilterPrivateNoCommand, manage_first_name),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["patronymic"]]) & FilterPrivateNoCommand, manage_patronymic),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["last_name"]]) & FilterPrivateNoCommand, manage_last_name),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["email"]]) & FilterPrivateNoCommand, manage_email),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["telefon"]]) & FilterPrivateNoCommand, manage_phone),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["date_of_birth"]]) & FilterPrivateNoCommand, manage_date_of_birth),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["main_photo"]]) & FilterPrivateNoCommand, manage_main_photo),
    #                 MessageHandler(Filters.text([PERSONAL_MENU["hobby"]]) & FilterPrivateNoCommand, manage_hobby),
    #                 # MessageHandler(Filters.text([PERSONAL_MENU["status"]]) & FilterPrivateNoCommand, manage_status),
    #                 MessageHandler(Filters.text([BACK_PROF["back"]]) & FilterPrivateNoCommand, go_start_conversation),
    #                 ],
            
    #         "working_busines_info":[                    
    #                 MessageHandler(Filters.text([BUSINES_MENU["company"]]) & FilterPrivateNoCommand, manage_company),
    #                 MessageHandler(Filters.text([BUSINES_MENU["employess_number"]]) & FilterPrivateNoCommand, manage_employess_number),
    #                 MessageHandler(Filters.text([BUSINES_MENU["job"]]) & FilterPrivateNoCommand, manage_job),
    #                 MessageHandler(Filters.text([BUSINES_MENU["branch"]]) & FilterPrivateNoCommand, manage_branch),
    #                 MessageHandler(Filters.text([BUSINES_MENU["city"]]) & FilterPrivateNoCommand, manage_city),
    #                 MessageHandler(Filters.text([BUSINES_MENU["site"]]) & FilterPrivateNoCommand, manage_site),
    #                 MessageHandler(Filters.text([BACK_PROF["back"]]) & FilterPrivateNoCommand, go_start_conversation),
    #                 ],
            
    #         "working_about_info":[                    
    #                 MessageHandler(Filters.text([ABOUT_MENU["about"]]) & FilterPrivateNoCommand, manage_about),
    #                 MessageHandler(Filters.text([ABOUT_MENU["sport"]]) & FilterPrivateNoCommand, manage_sport),
    #                 MessageHandler(Filters.text([ABOUT_MENU["hobby"]]) & FilterPrivateNoCommand, manage_hobby),
    #                 MessageHandler(Filters.text([BACK_PROF["back"]]) & FilterPrivateNoCommand, go_start_conversation),
    #                 ],

    #         "choose_action_first_name":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_first_name_action)],
    #         "choose_action_patronymic":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_patronymic_action)],
    #         "choose_action_last_name":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_last_name_action)],
    #         "choose_action_phone":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_phone_action)],
    #         "choose_action_about":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_about_action)],
    #         "choose_action_city":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_citi_action)],
    #         "choose_action_company":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_company_action)],
    #         "choose_action_employess_number":[
    #             MessageHandler(Filters.text & FilterPrivateNoCommand, manage_employess_number_action_message),
    #             CallbackQueryHandler(manage_employess_number_action_callback_query)
    #         ],
    #         "choose_action_job":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_action)],
    #         "choose_action_site":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_site_action)],
    #         "choose_action_inn":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_inn_action)],
    #         "choose_action_date_of_birth":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_date_of_birth_action)],
    #         "choose_action_email":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_email_action)],
    #         "choose_action_main_photo":[MessageHandler(Filters.photo & FilterPrivateNoCommand, manage_main_photo_action),
    #                                    MessageHandler(Filters.text & FilterPrivateNoCommand, manage_main_photo_txt_action)],
    #         "choose_action_job_region":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_job_region_action)],
    #         "choose_action_branch":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_branch_action)],
    #         "choose_action_sport":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_sport_action)],                         
    #         "choose_action_hobby":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_hobby_action)],
    #         "choose_action_referes":[MessageHandler(Filters.text & FilterPrivateNoCommand, manage_referes_action)],
    #         "delete_referes":[CallbackQueryHandler(delete_referes),
    #                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],
    #         "add_referes":[MessageHandler(Filters.text & FilterPrivateNoCommand, add_referes)],
    #         "select_referes":[CallbackQueryHandler(select_referes),
    #                        MessageHandler(Filters.text & FilterPrivateNoCommand, bad_callback_enter)],

    #     },
    #     # точка выхода из разговора
    #     fallbacks=[CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
    #                CommandHandler('start', stop_conversation, Filters.chat_type.private)]
    # )
    dp.add_handler(CallbackQueryHandler(view_profile, pattern="^profile$"))
    # dp.add_handler(conv_handler)   
