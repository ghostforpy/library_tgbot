# Generated by Django 4.1.8 on 2024-05-27 16:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("books", "0009_alter_userbookprogress_progress_txt"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="moderator_approved",
            field=models.BooleanField(
                default=False, verbose_name="Одобрено модератором"
            ),
        ),
    ]
