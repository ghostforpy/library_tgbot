# Generated by Django 4.1.8 on 2024-05-14 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tgbot", "0003_alter_tggroups_options"),
        ("books", "0003_delete_userbookprogress"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserBookProgress",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "progress_txt",
                    models.FloatField(
                        default=0.0,
                        help_text="Для книг типа TXT",
                        verbose_name="Прогресс",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Создано"),
                ),
                (
                    "book",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_progresses",
                        to="books.book",
                        verbose_name="Книга",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="readed_books",
                        to="tgbot.user",
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Прогресс",
                "verbose_name_plural": "Прогрессы",
            },
        ),
    ]