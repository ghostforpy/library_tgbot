import datetime
import pytz

import telegram

from config import celery_app

from tgbot.handlers.keyboard import make_keyboard
from tgbot.handlers.utils import send_mess_by_tmplt

from .models import MessagesToSend, MessageTemplates


@celery_app.task(bind=True,
                 name='msg.send_message',
                 default_retry_delay=30,
                 max_retries=6,
                 queue="msg_tasks",
                 )
def send_message(self):
    """
     Это задание рассылки сообщений. Повторяется с периодичностью заданной в задаче с кодом send_messages (10 сек)
     Сообщения беруться из таблицы MessagesToSend, куда добавляются другими заданиями или вручную   
    """
    mess_set = MessagesToSend.objects.filter(sended = False).order_by("created_at")[:20]
    for mess in mess_set:
        success = False
        reply_markup = None
        if  mess.reply_markup:
            buttons = mess.reply_markup.get("buttons")
            kb_type = mess.reply_markup.get("type")
            btn_in_row = mess.reply_markup.get("btn_in_row")
            first_btn = mess.reply_markup.get("first_btn")
            last_btn = mess.reply_markup.get("last_btn")
            reply_markup = make_keyboard(buttons,kb_type,btn_in_row,first_btn,last_btn)
        user_id = mess.receiver.user_id if mess.receiver else mess.receiver_user_id 

        success = send_mess_by_tmplt(user_id, mess, reply_markup)

        if type(success) != telegram.message.Message:
            mess.comment = str(success)
        else:
            mess.sended_at = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
        mess.sended = True
        mess.save()
    return {"sent": len(mess_set)}