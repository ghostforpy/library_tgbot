from django.contrib import admin

# Register your models here.
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "author",
        "created_at",
        "user_upload",
    )
    list_display_links = ("id",)
    list_select_related = ("user_upload",)
