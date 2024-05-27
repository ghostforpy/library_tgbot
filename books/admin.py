from django.contrib import admin

# Register your models here.
from .models import Book, UserBookProgress


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "created_at",
        "user_upload",
        "book_type",
        "moderator_approved",
    )
    list_display_links = ("id",)
    list_select_related = ("user_upload",)


@admin.register(UserBookProgress)
class UserBookProgressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "book",
        "user",
        "progress_txt",
    )
    list_display_links = ("id",)
    list_select_related = (
        "book",
        "user",
    )
    list_filter = (
        "user",
        "book",
    )
