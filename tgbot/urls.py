# -*- coding: utf-8 -*-

from django.conf import settings
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.contrib import admin
from . import views


app_name = "tgbot"


urlpatterns = [  
    path('', views.index, name="index"),
    path(settings.TELEGRAM_WEBHOOK, csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
