# Generated by Django 4.1.8 on 2024-05-14 17:39

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0002_book_book_type_userbookprogress"),
    ]

    operations = [
        migrations.DeleteModel(
            name="UserBookProgress",
        ),
    ]
