from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(MessagesToSend)
class MessagesToSendAdmin(admin.ModelAdmin) :
    list_display = ("receiver","text", "created_at", "sended_at","comment") 
    list_display_links = ("receiver","text" ) 
    search_fields = ("receiver",)
    readonly_fields = ["file_id","reply_markup"] 


class ForeingNameMessageTemplatesInline(admin.TabularInline):
    model = ForeingNameMessageTemplates


@admin.register(MessageTemplates)
class MessageTemplatesAdmin(admin.ModelAdmin) :
    readonly_fields = ["code","file_id"]
    list_display = ("code","name") 
    list_display_links = ("code","name" ) 
    search_fields = ("code","name")
    inlines = [
        ForeingNameMessageTemplatesInline,
    ]