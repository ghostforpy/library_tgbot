from config import celery_app

from tgbot.models import tgGroups
from tgbot.utils import send_message
from django.conf import settings
from telegram import Bot


bot = Bot(settings.TELEGRAM_TOKEN)

@celery_app.task(bind=True,
                 name='tasks.bot_available',
                 default_retry_delay=30,
                 max_retries=6)
def tasks_bot_available(self, bot_name=None):
    tg_group = tgGroups.objects.filter(name="BotsAvailable").first()
    if tg_group:
        if not bot_name:
            bot_name = bot.first_name
        send_message(
            tg_group.chat_id,
            f"Бот {bot_name} работает."
        )
    return {"status": "ok"}