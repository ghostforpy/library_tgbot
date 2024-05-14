import os
from telegram import (
    InlineQueryResultArticle,  
    ParseMode, InputTextMessageContent, Update)
from telegram.ext import (
    Dispatcher, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    Filters, ChosenInlineResultHandler,
    InlineQueryHandler, CallbackContext,
    # ConversationHandler
)
from tgbot.my_telegram.conversationhandler import MyConversationHandler as ConversationHandler
from tgbot.handlers.commands import command_start
from django.conf import settings
from .messages import *
from .answers import *
import tgbot.models as mymodels
from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.filters import FilterPrivateNoCommand
from tgbot.utils import mystr, send_message, send_photo, fill_file_id, send_contact
from tgbot.handlers.utils import get_no_foto_id
from tgbot.handlers.main.answers import get_start_menu
from tgbot.handlers.main.messages import get_start_mess

# Возврат к главному меню
def stop_conversation(update: Update, context: CallbackContext):
    # Заканчиваем разговор.
    if update.message:
        user_id = update.message.from_user.id
    else:
        query = update.callback_query
        query.answer()
        user_id = query.from_user.id
        query.edit_message_reply_markup(make_keyboard(EMPTY,"inline",1))

    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    context.user_data["search_started"] = False
    send_message(user_id=user_id, text=FIND_FINISH, reply_markup=make_keyboard(EMPTY,"usual",1))
    send_message(user_id=user_id, text=get_start_mess(user), reply_markup=get_start_menu(user))
    return ConversationHandler.END

# Временная заглушка
def blank(update: Update, context: CallbackContext):
    pass

def bad_callback_enter(update: Update, context: CallbackContext):
    update.message.reply_text(ASK_REENTER)
    return "working"

# Начало разговора
def start_conversation(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(
        update.callback_query.from_user.id
    )
    query = update.callback_query
    query.answer()
    if user.verified_by_admin and (user.course or user.is_on_course):
        text = HELLO_MESS_2[user.language]
        top_btns = FIND[user.language]
    elif user.course or user.is_on_course:
        text = HELLO_MESS_COURSE_NOT_APPROVED[user.language]
        top_btns = {}
    else:
        text = NO_COURSE_HELLO_MESS[user.language]
        top_btns = YES_NO[user.language]
    query.edit_message_text(
        text=text, 
        reply_markup=make_keyboard(
            top_btns,
            "inline",
            1,
            None,
            HOME[user.language]
        )
    )
    return "working" if user.verified_by_admin and (user.course or user.is_on_course) else "registration_for_the_course"

def yes_registration_course(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    update.callback_query.answer()
    user = mymodels.User.get_user_by_username_or_user_id(user_id)
    group = mymodels.tgGroups.get_group_by_name("Администраторы")
    if group:
        text = f"Пришла новая заявка на курсы от @{mystr(user.username)}\n"
        send_message(group.chat_id, text)
        if not user.username:
                send_contact(
                    user_id=group.chat_id,
                    phone_number=user.telefon,
                    first_name=user.first_name,
                    last_name=user.last_name
                )
    text = {
        "RU": "Ваша заявка отправлена",
        "UZ": "Sizning arizangiz yuborildi",
        "EN": "Your application has been sent",
    }[user.language]
    send_message(user_id=user.user_id, text=text)
    command_start(update, context)
    return ConversationHandler.END

# Обработчик поиска
def manage_find(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(
        update.inline_query.from_user.id
    )
    query = update.inline_query.query.strip()
    # if len(query) < 3:
    #     return
    users_set = mymodels.User.find_users_by_keywords(query)
    users_set = users_set.exclude(
        is_blocked_bot=True, 
        is_banned=True,
        user_id=update.inline_query.from_user.id
    )
    results = []
    msg = {
        "RU": "Выбран однокурсник",
        "UZ": "Kursdoshingiz",
        "EN": "Chosen однокурсник",
    }[user.language]
    for user in users_set:
        user_res_str = InlineQueryResultArticle(
            id=str(user.user_id),
            title=f'{user.first_name} {user.last_name}',
            input_message_content = InputTextMessageContent(msg),
            description = user.about,
        )
        if not settings.DEBUG:
            if user.main_photo != "":
                thumb_url = f'{settings.DOMAIN}{user.main_photo.url}'
            else:
                thumb_url = f"{settings.DOMAIN}/media/no_foto.jpg"
            user_res_str.thumb_url = thumb_url
            user_res_str.thumb_width = 25
            user_res_str.thumb_height = 25
        results.append(user_res_str)
    update.inline_query.answer(results, cache_time=5, auto_pagination=True)
    return "working"

def manage_chosen_user(update: Update, context: CallbackContext):
    user = mymodels.User.get_user_by_username_or_user_id(
        update.chosen_inline_result.from_user.id
    )
    chosen_user_id = update.chosen_inline_result.result_id
    chosen_user = mymodels.User.get_user_by_username_or_user_id(chosen_user_id)
    user_id = update.chosen_inline_result.from_user.id

    if not(chosen_user.main_photo):
        photo = settings.MEDIA_ROOT / 'no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        if not chosen_user.main_photo_id:
            fill_file_id(chosen_user, "main_photo")
        photo = chosen_user.main_photo.path
        photo_id = chosen_user.main_photo_id

    manage_usr_btn = make_manage_usr_btn(chosen_user_id, lang=user.language)

    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,HOME[user.language])
    text = chosen_user.full_profile(language=user.language)
    # text = chosen_user.short_profile()
    if os.path.exists(photo):
        send_photo(user_id, photo_id, caption=text, reply_markup=reply_markup)
    else:
        send_message(user_id=user_id, text = text, reply_markup=reply_markup)
    return "working"

def show_full_profile(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    found_user_id = int(data[-1])
    found_user = mymodels.User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

def handle_show_full_profile(update: Update, context: CallbackContext, found_user_id=None):
    if update.callback_query != None:
        query = update.callback_query
        user_id = query.from_user.id
        query.answer()
        if found_user_id == None:
            data = query.data.split("_")
            found_user_id = int(data[-1])
    else:
        user_id = update.message.from_user.id
    found_user = mymodels.User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)


    if not(found_user.main_photo):
        photo = settings.MEDIA_ROOT / 'no_foto.jpg'
        photo_id = get_no_foto_id()
    else:
        if not found_user.main_photo_id:
            fill_file_id(found_user, "main_photo")
        photo = found_user.main_photo.path
        photo_id = found_user.main_photo_id
    if os.path.exists(photo):
        send_photo(user_id, photo_id, caption=profile_text, reply_markup=reply_markup)
    else:
        send_message(user_id=user_id, text = profile_text, reply_markup=reply_markup)

    # send_message(query.from_user.id, text=profile_text, reply_markup=reply_markup)
    # query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    # try:
    #     # профиль с фотографией
    #     query.edit_message_caption(caption=profile_text, reply_markup=reply_markup)
    # except:
    #     # профиль без фотографии
    #     query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

def back_to_user(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    found_user_id = int(data[-1])
    found_user = mymodels.User.get_user_by_username_or_user_id(found_user_id)
    profile_text = found_user.full_profile()
    # profile_text = found_user.short_profile()
    manage_usr_btn = make_manage_usr_btn(found_user_id)
    reply_markup=make_keyboard(manage_usr_btn,"inline",1,None,BACK)
    query.edit_message_text(text=profile_text, reply_markup=reply_markup)
    return "working"

# Запрос телефона
def direct_communication(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    choosen_user_id = int(data[-1])
    choosen_user = mymodels.User.get_user_by_username_or_user_id(choosen_user_id)
    send_contact(
        user_id=query.from_user.id,
        phone_number=choosen_user.telefon,
        first_name=choosen_user.first_name,
        last_name=choosen_user.last_name
    )
    return


def setup_dispatcher_conv(dp: Dispatcher):
    # Диалог отправки сообщения
    conv_handler = ConversationHandler( 
        # точка входа в разговор      
        entry_points=[CallbackQueryHandler(start_conversation, pattern="^find_members$"),
                      CallbackQueryHandler(show_full_profile, pattern="^full_profile_"),
                      CallbackQueryHandler(handle_show_full_profile, pattern="^handle_full_profile_"),
                      CallbackQueryHandler(direct_communication, pattern="^direct_communication_"),
                     ],
        # этапы разговора, каждый со своим списком обработчиков сообщений
        states={
            "working":[
                       InlineQueryHandler(manage_find),
                       ChosenInlineResultHandler(manage_chosen_user),
                       CallbackQueryHandler(stop_conversation, pattern="^back$"),
                       CallbackQueryHandler(show_full_profile, pattern="^full_profile_"),
                       CallbackQueryHandler(direct_communication, pattern="^direct_communication_"),
                       CallbackQueryHandler(handle_show_full_profile, pattern="^handle_full_profile_"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ],
            "registration_for_the_course":[
                       CallbackQueryHandler(yes_registration_course, pattern="^yes$"),
                       CallbackQueryHandler(stop_conversation, pattern="^no"),
                       MessageHandler(Filters.text & FilterPrivateNoCommand, blank)
                      ]
        },
        # точка выхода из разговора
        fallbacks=[
            # MessageHandler(
            #     Filters.text & FilterPrivateNoCommand,
            #     blank
            # ),
            CommandHandler('cancel', stop_conversation, Filters.chat_type.private),
            CommandHandler('start', stop_conversation, Filters.chat_type.private)
        ]        
    )
    dp.add_handler(conv_handler)  
