from django.db import models
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.forms import Textarea, NumberInput

# from excel_response import ExcelResponse

from .models import *
from tgbot.forms import BroadcastForm
from sheduler.models import MessagesToSend


class UsertgGroupsInline(admin.TabularInline):
    model = UsertgGroups


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    readonly_fields = [
        "avatar_tag",
        "user_id",
        "username",
        "main_photo_id",
    ]  # Be sure to read only mode
    list_display = [
        "user_id",
        "username",
        "first_name",
        "last_name",
        "created_at",
        "is_blocked_bot",
        "comment",
    ]
    list_display_links = ["user_id", "username", "first_name", "last_name"]
    list_filter = [
        "is_blocked_bot",
        "is_banned",
        "verified_by_admin",
        "is_admin",
    ]
    search_fields = ("username", "user_id", "first_name", "last_name", "patronymic")
    fields = [
        ("user_id", "username"),
        ("last_name", "first_name", "patronymic", "date_of_birth"),
        ("avatar_tag", "main_photo", "telefon", "email", "main_photo_id"),
        (
            "is_blocked_bot",
            "is_banned",
            "is_admin",
            "is_moderator",
            "verified_by_admin",
        ),
        "about",
        "sport",
        "hobby",
        "comment",
        "language",
    ]
    inlines = [UsertgGroupsInline]
    formfield_overrides = {
        models.IntegerField: {"widget": NumberInput(attrs={"size": "20"})},
        models.TextField: {"widget": Textarea(attrs={"rows": 2, "cols": 100})},
    }
    actions = [
        "broadcast",
    ]
    ordering = ["last_name", "first_name"]

    def invited_users(self, obj):
        return obj.invited_users().count()

    @admin.action(description="Разослать сообщения")
    def broadcast(self, request, queryset):
        """Select users via check mark in django-admin panel, then select "Broadcast" to send message"""
        if "apply" in request.POST:
            broadcast_message_text = request.POST["broadcast_text"]

            for user in queryset:
                new_mess = MessagesToSend()
                new_mess.receiver = user
                new_mess.text = broadcast_message_text
                new_mess.save()
            self.message_user(
                request, "Broadcasting of %d messages has been started" % len(queryset)
            )

            return HttpResponseRedirect(request.get_full_path())

        form = BroadcastForm(
            initial={"_selected_action": queryset.values_list("user_id", flat=True)}
        )
        return render(
            request,
            "admin/broadcast_message.html",
            {"items": queryset, "form": form, "title": " "},
        )


# @admin.register(NewUser)
# class NewUserAdmin(admin.ModelAdmin):
#     list_display = ("user_id", "username", "first_name", "last_name", "registered")
#     list_display_links = (
#         "user_id",
#         "username",
#         "first_name",
#         "last_name",
#     )
#     search_fields = (
#         "user_id",
#         "username",
#         "first_name",
#         "last_name",
#     )
#     list_filter = [
#         "registered",
#     ]


@admin.register(tgGroups)
class tgGroupsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "chat_id",
        "link",
        "show_for_users",
        "send_new_users",
        "send_advertisements",
    )
    list_display_links = ("name",)
    list_editable = (
        "show_for_users",
        "send_new_users",
        "send_advertisements",
    )
    search_fields = ("name",)
    readonly_fields = ["file_id"]
