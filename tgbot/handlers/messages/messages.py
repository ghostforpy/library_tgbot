from django.utils.translation import gettext as _

from tgbot.handlers.main.messages import back_btn


start_send_messages_btn = lambda: {"start_send_messages": back_btn()}
enter_message_text = lambda: _("Введите текст сообщения")
message_from = lambda username, text: _("Сообщение от ") + str(username) + f":\n{text}"
message_sent = lambda: _("Сообщение отправлено.")