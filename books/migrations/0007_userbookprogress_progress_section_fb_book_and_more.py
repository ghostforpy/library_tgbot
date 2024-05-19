# Generated by Django 4.1.8 on 2024-05-16 18:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0006_userbookprogress_total_pages_txt_book_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userbookprogress",
            name="progress_section_fb_book",
            field=models.IntegerField(
                default=1, help_text="Для книг типа FB2", verbose_name="Прогресс глав"
            ),
        ),
        migrations.AddField(
            model_name="userbookprogress",
            name="total_sections_fb_book",
            field=models.IntegerField(
                default=1,
                help_text="Для книг типа FB2",
                verbose_name="Общее количество глав",
            ),
        ),
    ]