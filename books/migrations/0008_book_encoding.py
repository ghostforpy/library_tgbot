# Generated by Django 4.1.8 on 2024-05-19 11:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0007_userbookprogress_progress_section_fb_book_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="encoding",
            field=models.CharField(
                blank=True,
                default="",
                max_length=30,
                null=True,
                verbose_name="Кодировка",
            ),
        ),
    ]