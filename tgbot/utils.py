# -*- coding: utf-8 -*-

import datetime
import logging
import uuid
import re
import os
import random
import string
import telegram
from telegram import MessageEntity

from django.conf import settings

logger = logging.getLogger('default')


def extract_user_data_from_update(update):
    """ python-telegram-bot's Update instance --> User info """
    if update.message is not None:
        user = update.message.from_user.to_dict()
    elif update.inline_query is not None:
        user = update.inline_query.from_user.to_dict()
    elif update.chosen_inline_result is not None:
        user = update.chosen_inline_result.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.from_user is not None:
        update.callback_query.answer()
        user = update.callback_query.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.message is not None:
        user = update.callback_query.message.chat.to_dict()
    elif update.poll_answer is not None:
        user = update.poll_answer.user.to_dict()
    else:
        raise Exception(f"Can't extract user data from update: {update}")

    return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )


def get_chat_id(update, context):
    """Extract chat_id based on the incoming object."""

    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id


def get_file_path(instance, filename):
    """Create random unique filename for files, uploaded via admin."""

    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return filename


def convert_2_user_time(date: datetime.datetime):
    """Получает дату в UTC. Возвращает в Мск."""

    return date + datetime.datetime.timedelta(hours=3)

def is_date(str_date: str):
    try:
        date = datetime.datetime.strptime(str_date,"%d.%m.%Y")
        return date
    except Exception:
        return False

def is_email(email: str):
    email = email.replace(" ", "")
    email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
    if email_regex.match(email):
        return email
    else:
        return False

def mystr(val)->str:
    if val == None:
        return ""
    else:
        if isinstance(val,datetime.date):
            return val.strftime("%d.%m.%Y")
        elif isinstance(val,datetime.datetime):
            return val.strftime("%H:%M, %d.%m.%Y")
        else:
            return str(val)

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))

def get_uniq_file_name(path, name, ext):
    for num in range(999999):
        filename = f"{path}/{name}-{num}.{ext}"
        if not os.path.exists(filename):
            return f"{name}-{num}.{ext}"

ALL_TG_FILE_TYPES = ["document", "video_note", "voice", "sticker", "audio", "video", "animation", "photo"]

def _get_file_id(m):
    """ extract file_id from message (and file type?) """

    for doc_type in ALL_TG_FILE_TYPES:
        if (m[doc_type] != None) and (doc_type != "photo"):
            return m[doc_type]["file_id"], m[doc_type]["file_name"]

    if len(m["photo"]) > 0:
        best_photo = m["photo"][-1]
        return best_photo["file_id"], "userfoto.jpg"
    return None, None

def _get_all_file_id(m):
    for doc_type in ALL_TG_FILE_TYPES:
        if (m[doc_type] != None):
            return m[doc_type]["file_id"], m[doc_type]["file_name"]

    return None, None

def send_message(user_id, text, parse_mode=telegram.ParseMode.HTML, reply_markup=None, reply_to_message_id=None,
                 disable_web_page_preview=True, entities=None, api_kwargs = None, tg_token=settings.TELEGRAM_TOKEN,
                 disable_notification=None):
    bot = telegram.Bot(tg_token)
    try:
        if entities:
            entities = [
                MessageEntity(type=entity['type'],
                              offset=entity['offset'],
                              length=entity['length']
                )
                for entity in entities
            ]

        m = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
            disable_notification=disable_notification,
            api_kwargs = api_kwargs
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def send_photo(user_id, photo, caption=None, disable_notification=None, reply_to_message_id=None, 
               reply_markup=None, timeout=20, parse_mode=telegram.ParseMode.HTML, api_kwargs=None, allow_sending_without_reply=None, 
               caption_entities=None, filename=None, protect_content=None, tg_token=settings.TELEGRAM_TOKEN):

    text = None
    if caption and len(caption)>1023:
        text = caption
        reply_markup_txt = reply_markup
        caption = None
        reply_markup = None

    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_photo(
            chat_id=user_id,
            photo=photo,
            caption=caption, 
            disable_notification=disable_notification, 
            reply_to_message_id=reply_to_message_id, 
            reply_markup=reply_markup, 
            timeout=timeout, 
            parse_mode=parse_mode, 
            api_kwargs=api_kwargs, 
            allow_sending_without_reply=allow_sending_without_reply, 
            caption_entities=caption_entities, 
            filename=filename, 
            protect_content=protect_content
        )
        if text:
            send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def send_document(user_id, document, filename=None, caption=None, disable_notification=None, reply_to_message_id=None, 
            reply_markup=None, timeout=20, parse_mode=telegram.ParseMode.HTML, thumb=None, api_kwargs=None, 
            disable_content_type_detection=None, allow_sending_without_reply=None, caption_entities=None, 
            protect_content=None, tg_token=settings.TELEGRAM_TOKEN):

    text = None
    if caption and len(caption)>1023:
        text = caption
        reply_markup_txt = reply_markup
        caption = None
        reply_markup = None
    bot = telegram.Bot(tg_token)
    try:

        m = bot.send_document(
            chat_id=user_id,
            document=document,
            filename=filename, 
            caption=caption, 
            disable_notification=disable_notification, 
            reply_to_message_id=reply_to_message_id, 
            reply_markup=reply_markup, 
            timeout=timeout, 
            parse_mode=parse_mode, 
            thumb=thumb, 
            api_kwargs=api_kwargs, 
            disable_content_type_detection=disable_content_type_detection, 
            allow_sending_without_reply=allow_sending_without_reply, 
            caption_entities=caption_entities, 
            protect_content=protect_content
        )
        if text:
            send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
    return success

def send_video(user_id, video, duration=None, caption=None, disable_notification=None, 
               reply_to_message_id=None, reply_markup=None, timeout=20, width=None, height=None, 
               parse_mode=telegram.ParseMode.HTML, supports_streaming=None, thumb=None, api_kwargs=None, 
               allow_sending_without_reply=None, caption_entities=None, filename=None, 
               protect_content=None, tg_token=settings.TELEGRAM_TOKEN):

    text = None
    if caption and len(caption)>1023:
        text = caption
        reply_markup_txt = reply_markup
        caption = None
        reply_markup = None


    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_video(
            chat_id=user_id,
            video=video, 
            duration=duration, 
            caption=caption, 
            disable_notification=disable_notification, 
            reply_to_message_id=reply_to_message_id, 
            reply_markup=reply_markup, 
            timeout=timeout, 
            width=width, 
            height=height, 
            parse_mode=parse_mode, 
            supports_streaming=supports_streaming, 
            thumb=thumb, 
            api_kwargs=api_kwargs, 
            allow_sending_without_reply=allow_sending_without_reply, 
            caption_entities=caption_entities, 
            filename=filename, 
            protect_content=protect_content
        )
        if text:
            send_message(user_id=user_id, text=text, reply_markup=reply_markup_txt)
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def fill_file_id(obj, file_field: str, text: str = ""):
    """
    заполняет у объекта поле с телеграм ид файоа
    obj - оъект, file_field - имя поля с файлом
    имя поля с ид должно быть file_field + '_id'
    """

    file = getattr(obj, file_field)
    if not file:
        return
    if os.path.exists(file.path):
        file_ext = file.name.split(".")[-1]

        if file_ext in ["jpg","jpeg","png","gif","tif","tiff","bmp"]:
            mess = send_photo(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)
                    
        elif file_ext in ["mp4","avi","mov","mpeg"]:
            mess = send_video(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)
        else:
            mess = send_document(settings.TRASH_GROUP, open(file.path, 'rb'), caption = text)

        file_id, _ = _get_file_id(mess)
        setattr(obj, file_field + "_id", file_id)
        obj.save()

def send_contact(user_id, phone_number=None, first_name=None, last_name=None,
                 disable_notification=None,
                 reply_to_message_id=None, reply_markup=None, timeout=None, contact=None, vcard=None,
                 api_kwargs = None, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_contact(
            chat_id=user_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            vcard=vcard,
            contact=contact,
            disable_notification=disable_notification,
            timeout=timeout,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            api_kwargs = api_kwargs
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success

def send_media_group(user_id, media=None,
                 disable_notification=None,
                 reply_to_message_id=None, 
                 api_kwargs = None, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        m = bot.send_media_group(
            chat_id=user_id,
            media=media,
            disable_notification=disable_notification,
            reply_to_message_id=reply_to_message_id,
            api_kwargs = api_kwargs
        )
    except telegram.error.Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        success = f"Can't send message to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
    return success


def send_location(user_id, latitude=None, longitude=None, location=None, reply_markup=None, reply_to_message_id=None,
                 disable_notification=None, timeout=None, api_kwargs = None, live_period=None,
                horizontal_accuracy=None, heading=None, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    if not (latitude and longitude) and not location:
        raise telegram.error.BadRequest("Location or latitude and longitude required")
    try:
        m = bot.send_location(
            chat_id=user_id,
            latitude=latitude,
            longitude=longitude,
            disable_notification=disable_notification,
            reply_markup=reply_markup,
            location=location,
            timeout=timeout,
            live_period=live_period,
            horizontal_accuracy=horizontal_accuracy,
            heading=heading,
            reply_to_message_id=reply_to_message_id,
            api_kwargs = api_kwargs
        )
    except telegram.error.Unauthorized:
        print(f"Can't send location to {user_id}. Reason: Bot was stopped.")
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = f"Can't send location to {user_id}. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't send location to {user_id}. Reason: {e}")
        success = e
    else:
        success = m
        #User.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success



def delete_message(chat_id, message_id, tg_token=settings.TELEGRAM_TOKEN):
    bot = telegram.Bot(tg_token)
    try:
        m = bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    except telegram.error.Unauthorized:
        print(f"Can't delete message. Reason: Bot was stopped.")
        success = f"Can't delete message. Reason: Bot was stopped."
    except Exception as e:
        print(f"Can't delete message. Reason: {e}")
        success = e
    else:
        success = m
    return success