import re
from telegram.update import Update
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters,
    ChosenInlineResultHandler,
    InlineQueryHandler,
    # ConversationHandler,
)
# from telegram.ext.filters import Filters as F
from telegram import InlineQueryResultArticle, InputTextMessageContent, ReplyKeyboardRemove
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.translation import override as translation_override

from tgbot.my_telegram import MyConversationHandler as ConversationHandler

from .messages import *
from .answers import *
# from tgbot.handlers.main.messages import NO_ADMIN_GROUP
from tgbot.models import (
    Status,
    User,
    # tgGroups,
    NewUser
)
# from sheduler.models import MessageTemplates

from tgbot.utils import _get_file_id
from tgbot.handlers.utils import send_photo

from tgbot.handlers.keyboard import make_keyboard
# from tgbot.handlers.main.answers import get_start_menu
# from tgbot.handlers.main.messages import get_start_mess
from tgbot import utils
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.utils import send_message
from .steps import STEPS
from .saveuser import end_registration


def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    context.user_data.clear()
    keyboard = make_keyboard(START,"usual",1)
    update.message.reply_text(REGISTRATION_CANCELED, reply_markup=keyboard)
    return ConversationHandler.END

def start_conversation(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
        update.callback_query.answer()
    new_user, _ = NewUser.objects.get_or_create(user_id=user_id)
    # проверяем есть ли у пользователя в Телеграмм имя пользователя
    # if new_user.username is None:
    #     update.message.reply_text(USERNAME_NEEDED)
    #     stop_conversation(update, context)
    #     return ConversationHandler.END
    # update.message.reply_text(WELCOME_REG)
    # send_message(user_id, WELCOME_REG[new_user.language])
    # prepare_ask_first_name(update, new_user)
    f = STEPS["FIRSTNAME"]["self_prepare"]
    f(update, context, new_user)
    # update.message.reply_text(WELCOME_REG, reply_markup=make_keyboard(APPROVAL_ANSWERS,"usual",2))
    return STEPS["FIRSTNAME"]["step"]

def continue_registration(update: Update, context: CallbackContext):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        update.callback_query.answer()
    else:
        user_id = update.message.from_user.id
    new_user, _ = NewUser.objects.get_or_create(user_id=user_id)
    step = new_user.step
    if step:
        if step in ["COURSE_EXPECTATIONS"]:
            f = STEPS[step]["self_prepare"]
            f(update, context, new_user)
            return STEPS[step]["step"]
        else:
            f = STEPS[step]["prepare"]
            f(update, context, new_user)
            return STEPS[step]["next"]
    else:
        f = STEPS["FIRSTNAME"]["self_prepare"]
        f(update, context, new_user)
        return STEPS["FIRSTNAME"]["step"]

def cancel_registration(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    update.callback_query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    with translation_override(new_user.language):
        text = registration_canceled()
    new_user.delete()
    send_message(user_id, text=text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def back(update: Update, context: CallbackContext):
    if update.message:
        user_id = update.message.from_user.id
    if update.callback_query:
        update.callback_query.answer()
        user_id = update.callback_query.from_user.id
    new_user = NewUser.objects.get(user_id = user_id)
    step = new_user.step
    step_back = 2 if step == "COURSE_EXPECTATIONS" else 1
    for i in STEPS:
        if STEPS[i]["step"] == STEPS[step]["step"] - step_back:
            new_user.step = i
            new_user.save()
            break
    with translation_override(new_user.language):
        text = _("Предыдущий вопрос")
    send_message(new_user.user_id, text=text, reply_markup=ReplyKeyboardRemove())
    f = STEPS[step]["self_prepare"]
    f(update, context, new_user, new_message=True)
    return STEPS[step]["step"]
    # return start_conversation(update, context)

def back_other(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    query = update.callback_query
    query.answer()
    step = new_user.step
    f = STEPS[step]["prepare"]
    f(update, context, new_user)
    return STEPS[step]["next"]

def processing_language(update: Update, context: CallbackContext):
    if update.message is not None:
        update.message.reply_text(
            "Используйте предложенные варианты.",
            reply_markup=make_keyboard({},"usual",2)
        )
        f = STEPS["LANGUAGE"]["self_prepare"]
        f(update, context, None)
        return
    query = update.callback_query
    variant = query.data
    query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    new_user.language = variant
    context.user_data["language"] = new_user.language
    new_user.step = "LANGUAGE"
    new_user.save()
    f = STEPS["LANGUAGE"]["prepare"]
    f(update, context, new_user)
    return STEPS["LANGUAGE"]["next"]

def processing_firstname(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.first_name = update.message.text
    new_user.step = "FIRSTNAME"
    new_user.save()
    f = STEPS["FIRSTNAME"]["prepare"]
    f(update, context, new_user)
    return STEPS["FIRSTNAME"]["next"]

def processing_lastname(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.last_name = update.message.text
    new_user.step = "LASTNAME"
    new_user.save()
    f = STEPS["LASTNAME"]["prepare"]
    f(update, context, new_user)
    return STEPS["LASTNAME"]["next"]

def processing_patronymic(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.patronymic = update.message.text
    new_user.save()
    f = STEPS["PATRONYMIC"]["prepare"]
    f(update, context, new_user)
    return STEPS["PATRONYMIC"]["next"]


def skip_shop(update: Update, context: CallbackContext):
    update.callback_query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    new_user.step = "SHOP"
    new_user.save()
    if isinstance(STEPS["SHOP"]["next"], int):
        f = STEPS["SHOP"]["prepare"]
        f(update, context, new_user)
        return STEPS["SHOP"]["next"]
    else:
        return end_registration(update, context, new_user)


def shop_manage_find(update: Update, context: CallbackContext):
    query = update.inline_query.query.strip()
    # if len(query) < 3:
    #     return
    query = query.lower()
    new_user = NewUser.objects.get(user_id=update.inline_query.from_user.id)
    shops_set = Shop.find_shop_by_keywords(query)
    results = []
    with translation_override(new_user.language):
        msg = choose_shop_msg()
        for shop in shops_set:
            shop_res_str = InlineQueryResultArticle(
                id=str(shop.id),
                title=str(shop),
                input_message_content=InputTextMessageContent(msg),
                description = f"{shop.region_name} {shop.main_phone}",
            )
            results.append(shop_res_str)
    update.inline_query.answer(results, auto_pagination=True, cache_time=60)
    return STEPS["SHOP"]["step"]

def handle_chose_shop(update: Update, context: CallbackContext):
    pass

def manage_chosen_shop(update: Update, context: CallbackContext):
    chosen_shop_id = update.chosen_inline_result.result_id
    chosen_shop = Shop.objects.get(id=chosen_shop_id)
    user_id = update.chosen_inline_result.from_user.id
    new_user = NewUser.objects.get(user_id=user_id)
    new_user.shop = chosen_shop
    new_user.step = "SHOP"
    new_user.save()
    if isinstance(STEPS["SHOP"]["next"], int):
        f = STEPS["SHOP"]["prepare"]
        f(update, context, new_user)
        return STEPS["SHOP"]["next"]
    else:
        return end_registration(update, context, new_user)


def processing_status_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    variant = query.data
    query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    status = Status.objects.get(pk=variant)
    new_user.status = status
    new_user.step = "ROLE"
    new_user.save()
    if isinstance(STEPS["ROLE"]["next"], int):
        f = STEPS["ROLE"]["prepare"]
        f(update, context, new_user)
        return STEPS["ROLE"]["next"]
    else:
        return end_registration(update, context, new_user)


def processing_course_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    variant = query.data
    query.answer()
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    new_user.course = int(variant)
    new_user.completion_of_training = True
    new_user.step = "COURSE"
    new_user.save()
    if isinstance(STEPS["COURSE"]["next"], int):
        f = STEPS["COURSE"]["prepare"]
        f(update, context, new_user)
        return STEPS["COURSE"]["next"]
    else:
        return end_registration(update, context, new_user)

def processing_course_expectations(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    new_user.course_expectations = update.message.text
    new_user.save()
    if isinstance(STEPS["COURSE_EXPECTATIONS"]["next"], int):
        f = STEPS["COURSE_EXPECTATIONS"]["prepare"]
        f(update, context, new_user)
        return STEPS["COURSE_EXPECTATIONS"]["next"]
    else:
        return end_registration(update, context, new_user)


def processing_birhday(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    date = utils.is_date(update.message.text)
    if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
       stop_conversation(update, context)
       return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        f = STEPS["BIRTHDAY"]["prepare"]
        f(update, context, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return STEPS["BIRTHDAY"]["next"]
    elif not(date): # ввели неверную дату
        update.message.reply_text(BAD_DATE, reply_markup=make_keyboard(CANCEL,"usual",2))
        return
    else: # ввели верный дату
        new_user.date_of_birth = date
        new_user.save()
        f = STEPS["BIRTHDAY"]["prepare"]
        f(update, context, new_user)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_EMAIL + f"\n Уже введено: '{utils.mystr(new_user.email)}'", reply_markup=keyboard)
        return STEPS["BIRTHDAY"]["next"]

def processing_about(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.text == CANCEL["cancel"]:
        stop_conversation(update, context)
        return ConversationHandler.END
    elif update.message.text == CANCEL_SKIP["skip"]:
        f = STEPS["ABOUT"]["prepare"]
        f(update, context, new_user)
        # prepare_ask_birthday(update, new_user.date_of_birth)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{utils.mystr(new_user.date_of_birth)}'", reply_markup=keyboard)
        return STEPS["ABOUT"]["next"]
    else:
        new_user.about = update.message.text 
        new_user.save()
        f = STEPS["ABOUT"]["prepare"]
        f(update, context, new_user)
        # prepare_ask_birthday(update, new_user.date_of_birth)
        # keyboard = make_keyboard(CANCEL,"usual",2)
        # birthday = utils.mystr(new_user.date_of_birth)
        # update.message.reply_text(ASK_BIRHDAY + f"\n Уже введено: '{birthday}'", reply_markup=keyboard)
        return STEPS["ABOUT"]["next"]

def processing_site(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    # if update.message.text == CANCEL_SKIP["cancel"]: # решили прервать регистрацию
    #    stop_conversation(update, context)
    #    return ConversationHandler.END
    # # elif update.message.text == CANCEL_SKIP["skip"]:
    # #     site = ""
    # else:
    validate = URLValidator()
    site = update.message.text
    site = site.lower()
    if not site.startswith("https://") and not site.startswith("http://"):
        site = "http://" + site
    try:
        validate(site)
    except ValidationError:
        update.message.reply_text(BAD_SITE, reply_markup=make_keyboard({},"usual",2))
        return
    new_user.site = site
    new_user.save()
    f = STEPS["SITE"]["prepare"]
    f(update, context, new_user)
    return STEPS["SITE"]["next"]
    # return end_registration(update, context, new_user)

r = re.compile(r"^\+?\d{12}$")

def processing_phone(update: Update, context: CallbackContext):
    def save_phone(phone, new_user: NewUser):
        context.user_data["bad_phone_registration"] = False
        # Запоминаем телефон
        new_user.telefon = phone
        new_user.step = "PHONE"
        new_user.save()
        with translation_override(new_user.language):
            msg = _("Контакт принят")
        send_message(new_user.user_id, text=msg, reply_markup=ReplyKeyboardRemove())
        if isinstance(STEPS["PHONE"]["next"], int):
            f = STEPS["PHONE"]["prepare"]
            f(update, context, new_user)
            return STEPS["PHONE"]["next"]
        else:
            return end_registration(update, context, new_user)

    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    if update.message.contact != None: # Был прислан контакт
        return save_phone(update.message.contact.phone_number, new_user)
    elif r.match(update.message.text):
        return save_phone(update.message.text, new_user)
    else:
        f = STEPS["PHONE"]["self_prepare"]
        f(update, context, new_user)
        return

def processing_photo(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.message.from_user.id)
    foto_id, filename_orig = _get_file_id(update.message)
    filename_orig = str(new_user.user_id) + "-" + filename_orig
    filename_lst = filename_orig.split(".")
    newFile = context.bot.get_file(foto_id)
    filename = utils.get_uniq_file_name(f"{settings.MEDIA_ROOT}/user_fotos", filename_lst[0], filename_lst[1])
    newFile.download(f"{settings.MEDIA_ROOT}/user_fotos/{filename}")
    new_user.main_photo = "user_fotos/" + filename
    new_user.main_photo_id = foto_id
    new_user.step = "PHOTO"
    new_user.save()
    if isinstance(STEPS["PHOTO"]["next"], int):
        f = STEPS["PHOTO"]["prepare"]
        f(update, context, new_user)
        return STEPS["PHOTO"]["next"]
    else:
        return end_registration(update, context, new_user)

def processing_photo_message(update: Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id=update.message.from_user.id)
    with translation_override(new_user.language):
        update.message.reply_text(bad_photo())
    f = STEPS["PHOTO"]["self_prepare"]
    f(update, context, new_user)
    return

def processing_photo_callback(update:Update, context: CallbackContext):
    new_user = NewUser.objects.get(user_id = update.callback_query.from_user.id)
    update.callback_query.answer()
    new_user.main_photo = ""
    new_user.main_photo_id = ""
    new_user.step = "PHOTO"
    new_user.save()
    if isinstance(STEPS["PHOTO"]["next"], int):
        f = STEPS["PHOTO"]["prepare"]
        f(update, context, new_user)
        return STEPS["PHOTO"]["next"]
    else:
        return end_registration(update, context, new_user)

#-----------------------------------------------------------------------------
#----------------Manage new user----------------------------------------------

def stop_conversation_new_user(update: Update, context: CallbackContext):
    """ 
       Возврат к главному меню    
    """
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        # query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))
        # query.edit_message_text("Подтверждение завершено", reply_markup=make_keyboard(EMPTY,"inline",1))
        query.delete_message()

    # user = User.get_user_by_username_or_user_id(user_id)
    # send_message(user_id=user_id, text=FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    # send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    # return ConversationHandler.END

def manage_new_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id
    user = User.get_user_by_username_or_user_id(user_id)

    if (not user) or (not user.is_admin):
        text ="{}, у Вас нет прав администратора".format(query.from_user.full_name)
        send_message(update.callback_query.message.chat_id, text)
        return
    query_data = query.data.split("-")
    new_user_id = int(query_data[1])
    new_user = User.get_user_by_username_or_user_id(new_user_id)

    profile_text = new_user.full_profile()

    photo_id = new_user.main_photo_id
    if not new_user.verified_by_admin:
        manage_usr_btn = {
            f"confirm_reg-{new_user_id}":"Подтвердить регистрацию",
            # f"uncofirm_reg-{new_user_id}":"Отклонить регистрацию",
            # f"back_from_user_confirm-{new_user_id}":"Отмена обработки",
        }
        reply_markup = make_keyboard(manage_usr_btn,"inline",1)
    else:
        reply_markup = None
    # send_message(user_id=user_id, text=profile_text)
    send_photo(user_id=user_id, photo=photo_id, caption=profile_text, reply_markup=reply_markup)

    
    # send_message(user_id = user_id, text=profile_text, reply_markup=reply_markup)

    # bn = {f"manage_new_user-{new_user.user_id}":"Посмотреть пользователя"}
    # reply_markup =  make_keyboard(bn,"inline",1)       
    # text = query.message.text.split('\n')[0]
    # text += f'\nПрофиль пользователя отправлен в чат {context.bot.name} '
    # text += f'пользователю {query.from_user.full_name}'
    # query.edit_message_text(text=text, reply_markup=reply_markup)

    return

def confirm_registration(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    # user_id = query.from_user.id
    # user = User.get_user_by_username_or_user_id(user_id)
    query_data = query.data.split("-")
    new_user_id = int(query_data[1])
    new_user = User.get_user_by_username_or_user_id(new_user_id)
    new_user.is_blocked_bot = False
    new_user.verified_by_admin = True
    new_user.comment = "Регистрация подтверждена"
    new_user.save()
    # text = MessageTemplates.objects.get(code=MessageTemplatesCode.PROFILE_APPROVED)
    with translation_override(new_user.language):
        text = _("Учетная запись подтверждена")
    send_message(new_user.user_id, text)
    query.delete_message()


    # groups = tgGroups.objects.filter(send_new_users=True)
    # if groups.count() == 0:
    #     update.message.reply_text(NO_SEND_NEW_USERS_GROUPS)
    # else:
    #     for group in groups:
    #         bn = {f"handle_full_profile_{new_user.user_id}":"Познакомиться"}
    #         reply_markup =  make_keyboard(bn,"inline",1)
    #         # reply_markup =  make_keyboard(bn,"inline",1)
    #         # text = new_user.new_user_notification()
    #         # text =f"Познакомьтесь с новым участником группы\n @{utils.mystr(new_user.username)} {new_user.first_name} {utils.mystr(new_user.last_name)}"
    #         # utils.send_message(group.chat_id, text, reply_markup=reply_markup)
    #         utils.send_photo(
    #             group.chat_id,
    #             new_user.main_photo_id,
    #             new_user.full_profile(),
    #             reply_markup=reply_markup
    #             )


def setup_dispatcher_conv(dp: Dispatcher):
    conv_handler_reg = ConversationHandler( # здесь строится логика разговора
        persistent=True,
        name="registration_conversation",
        conversation_timeout=60*60*12, # 12 hours
        # точка входа в разговор
        entry_points=[
            # MessageHandler(
                # Filters.text(REGISTRATION_START_BTN[i]["reg_start"]) & FilterPrivateNoCommand, start_conversation
            # ) for i in REGISTRATION_START_BTN
                CallbackQueryHandler(start_conversation, pattern="^reg_start$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
        ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            # STEPS["LANGUAGE"]["step"]:[
            #     CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
            #     CallbackQueryHandler(processing_language),
            #     MessageHandler(Filters.text & FilterPrivateNoCommand, processing_language)
            # ],
            STEPS["FIRSTNAME"]["step"]:[
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_firstname)
            ],
            STEPS["LASTNAME"]["step"]:[
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
                CallbackQueryHandler(back, pattern="^back$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, processing_lastname)
            ],
            # STEPS["SHOP"]["step"]: [
            #     InlineQueryHandler(shop_manage_find),
            #     ChosenInlineResultHandler(manage_chosen_shop),
            #     CallbackQueryHandler(back, pattern="^back$"),
            #     CallbackQueryHandler(skip_shop, pattern="^skip$"),
            #     MessageHandler(
            #         Filters.regex(
            #             '|'.join(
            #                 [
            #                     f'^{CHOOSE_SHOP_MSG[i]}$' for i in CHOOSE_SHOP_MSG
            #                 ]
            #             )
            #         ) & FilterPrivateNoCommand,
            #         handle_chose_shop
            #     ),
            #     MessageHandler(Filters.text & FilterPrivateNoCommand, continue_registration),
            # ],
            STEPS["PHONE"]["step"]: [
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
                MessageHandler((Filters.regex('|'.join([f'^{STEP_BACK[i]["back"]}$' for i in STEP_BACK])) & Filters.text) & FilterPrivateNoCommand, back),
                MessageHandler((Filters.contact | Filters.text) & FilterPrivateNoCommand, processing_phone)
            ],
            STEPS["ROLE"]["step"]: [
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
                CallbackQueryHandler(back, pattern="^back$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
                CallbackQueryHandler(processing_status_callback, pattern="^\d+$"),
                MessageHandler(Filters.text & FilterPrivateNoCommand, continue_registration)
            ],
            STEPS["PHOTO"]["step"]:[
                CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
                CallbackQueryHandler(back, pattern="^back$"),
                CallbackQueryHandler(continue_registration, pattern="^continue_registration$"),
                MessageHandler(Filters.photo & FilterPrivateNoCommand, processing_photo),
                MessageHandler((Filters.text | Filters.update) & FilterPrivateNoCommand, processing_photo_message),
                CallbackQueryHandler(processing_photo_callback, pattern="^skip$"),
            ],
        },
        # точка выхода из разговора
        fallbacks=[
            CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"),
            CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
            CommandHandler('start', stop_conversation, Filters.chat_type.private)
            ]
    )
    dp.add_handler(conv_handler_reg)

    dp.add_handler(CallbackQueryHandler(cancel_registration, pattern="^cancel_registration$"))
    dp.add_handler(CallbackQueryHandler(manage_new_user, pattern="^manage_new_user-"))
    # dp.add_handler(CallbackQueryHandler(stop_conversation_new_user, pattern="^back_from_user_confirm-"))
    dp.add_handler(CallbackQueryHandler(confirm_registration, pattern="^confirm_reg-"))
    # dp.add_handler(CallbackQueryHandler(stop_conversation_new_user, pattern="^uncofirm_reg-"))
     
    # conv_handler_confirm_reg = ConversationHandler( 
    #     # точка входа в разговор
    #     entry_points=[CallbackQueryHandler(manage_new_user, pattern="^manage_new_user-")],
    #     states={
    #         "wait_new_user_comand":[                                  
    #                    CallbackQueryHandler(stop_conversation_new_user, pattern="^back$"),
    #                    CallbackQueryHandler(confirm_registration, pattern="^confirm_reg-"),
    #                    CallbackQueryHandler(stop_conversation_new_user, pattern="^uncofirm_reg-"),
    #                   ],
    #     },
    #     # точка выхода из разговора
    #     fallbacks=[CommandHandler('cancel', stop_conversation_new_user, Filters.chat_type.private),
    #                CommandHandler('start', stop_conversation_new_user, Filters.chat_type.private)]
    # )
    # dp.add_handler(conv_handler_confirm_reg)
