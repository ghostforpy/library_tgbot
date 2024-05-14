import json
# import logging
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render

# from django.conf import settings

from tgbot.handlers.dispatcher import process_telegram_event, TELEGRAM_BOT_USERNAME

# logger = logging.getLogger(__name__)


BOT_URL = f"https://t.me/{TELEGRAM_BOT_USERNAME}"


def index(request):
    return render(request, 'main/index.html')

class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again. 
    # Can be fixed with async task execution
    def post(self, request, *args, **kwargs):
        process_telegram_event(json.loads(request.body))
        return JsonResponse({"ok": "POST request processed"})
    
    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request processed. But nothing done"})
