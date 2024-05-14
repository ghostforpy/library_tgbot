# -*- coding: utf-8 -*-

from django.db.models import Q, Avg
from django.urls import reverse
from django.conf import settings

from typing import Tuple, Optional

from django.db import models
from django.db.models.functions import Concat

from django.utils.translation import gettext_lazy as _
from django.utils.translation import override as translation_override
from django.utils.safestring import mark_safe

# from django.core.exceptions import ValidationError
from utils.get_url_model import GetUrlModelMixin

from .utils import get_no_foto_id
from tgbot.utils import mystr, extract_user_data_from_update, _get_file_id, send_photo

# from .utils import get_model_text
from .language import LANGUAGE, DEFAULT_LANGUAGE


class AbstractTgUser(models.Model, GetUrlModelMixin):
    LANGUAGE = LANGUAGE
    DEFAULT_LANGUAGE = DEFAULT_LANGUAGE
    # Личная инфо:
    user_id = models.BigIntegerField(primary_key=True)
    username = models.CharField(
        _("Телеграм логин"), max_length=32, null=True, blank=True
    )
    last_name = models.CharField(_("Фамилия"), max_length=256, null=True, blank=True)
    first_name = models.CharField(_("Имя"), max_length=256)
    patronymic = models.CharField(_("Отчество"), max_length=150, null=True, blank=True)
    email = models.EmailField(_("E-mail"), max_length=100, null=True, blank=True)
    telefon = models.CharField(_("Телефон"), max_length=13, null=True, blank=True)
    date_of_birth = models.DateField(_("Дата рождения"), null=True, blank=True)
    main_photo = models.ImageField(
        _("Основное фото"), upload_to="user_fotos", null=True, blank=True
    )
    main_photo_id = models.CharField(
        _("id основного фото"), max_length=150, null=True, blank=True
    )

    # О себе:
    about = models.TextField(_("О себе"), null=True, blank=True)

    # Дополнительные поля
    created_at = models.DateTimeField(_("Создан"), auto_now_add=True)
    language_code = models.CharField(
        max_length=8, null=True, blank=True, help_text=_("Telegram client's lang")
    )
    registered = models.BooleanField(_("Зарегистрирован"), default=False)
    language = models.CharField(
        _("Выбранный язык"), max_length=50, default=DEFAULT_LANGUAGE, choices=LANGUAGE
    )

    class Meta:
        abstract = True

    def __str__(self):
        res = [str(self.first_name), str(self.last_name)]
        if self.username is not None:
            res.insert(0, f"@{self.username}")
        res = " ".join(res)
        return res

    @property
    def name(self):
        return " ".join([str(self.first_name), str(self.last_name)])


# class NewUser(AbstractTgUser):
#     step = models.CharField(_("Завершенный шаг регистрации"), max_length=50, default="")

#     class Meta:
#         verbose_name = _("Новый пользователь")
#         verbose_name_plural = _("Новые пользователи")


class UserQuerySet(models.QuerySet):
    def annotate_uname(self):
        return self.annotate(
            uname=Concat(
                "first_name",
                models.Value(" "),
                "last_name",
                output_field=models.CharField(),
            )
        )

    def find_users_by_keywords(self, keywords):
        """осуществляет поиск участников, у которых в любом поле упоминаются ключевые слова"""
        q = (
            Q(username__icontains=keywords)
            | Q(last_name__icontains=keywords)
            | Q(first_name__icontains=keywords)
            | Q(patronymic__icontains=keywords)
            | Q(telefon__icontains=keywords)
            | Q(email__icontains=keywords)
            | Q(about__icontains=keywords)
            | Q(comment__icontains=keywords)
            | Q(sport__icontains=keywords)
            | Q(hobby__icontains=keywords)
        )
        return self.filter(q).distinct()

    def get_user_by_username_or_user_id(self, string) -> Optional["User"]:
        """Search user in DB, return User or None if not found"""
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return self.filter(user_id=int(username)).first()
        return self.filter(username__iexact=username).first()


class UserManager(models.Manager):
    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db).annotate_uname()

    def find_users_by_keywords(self, keywords):
        return self.get_queryset().find_users_by_keywords(keywords)

    def annotate_uname(self):
        return self.get_queryset().annotate_uname()

    def get_user_by_username_or_user_id(self, string):
        return self.get_queryset().get_user_by_username_or_user_id(string)


class User(AbstractTgUser):

    is_blocked_bot = models.BooleanField(_("Заблокирован"), default=False)
    is_banned = models.BooleanField(_("Забанен"), default=False)
    is_admin = models.BooleanField(_("Администратор"), default=False)
    is_moderator = models.BooleanField(_("Модератор"), default=False)

    # О себе:
    sport = models.TextField(_("Спорт"), null=True, blank=True)
    hobby = models.TextField(_("Хобби"), null=True, blank=True)
    needs = models.TextField(_("Потребности"), null=True, blank=True)
    comment = models.TextField(_("Комментарий"), null=True, blank=True)

    # Дополнительные поля
    updated_at = models.DateTimeField(_("Изменен"), auto_now=True)
    verified_by_admin = models.BooleanField(
        _("Проверен администратором"), default=False
    )

    objects = UserManager()

    # def clean(self):
    #     if self.chief:
    #         if self.is_chief_of(self.chief_id):
    #             raise ValidationError({
    #                     'chief': _('Подчиненный не может быть начальником'),
    #                 })
    #     return super().clean()

    def save(self, *args, **kwargs) -> None:
        def fill_main_photo_id():
            mess = send_photo(
                settings.TRASH_GROUP,
                photo=self.main_photo,
            )
            main_photo_id, _ = _get_file_id(mess)
            self.main_photo_id = main_photo_id

        if not self.main_photo:
            self.main_photo_id = get_no_foto_id()
        else:
            if self.pk:
                main_photo = User.objects.get(pk=self.pk).main_photo
                if main_photo:
                    if self.main_photo.size != main_photo.size:
                        fill_main_photo_id()
                else:
                    fill_main_photo_id()
            else:
                fill_main_photo_id()
        return super().save(*args, **kwargs)

    # Here I return the avatar or picture with an owl, if the avatar is not selected
    def get_avatar(self):
        if not self.main_photo:
            return "/media/no_foto.jpg"
        return self.main_photo.url

    # method to create a fake table field in read only mode width="100"
    def avatar_tag(self):
        return mark_safe('<img src="%s" height="150" />' % self.get_avatar())

    def get_admin_url(self):
        return reverse(
            "admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name),
            args=(self.user_id,),
        )

    @classmethod
    def get_user_and_created(cls, update, context) -> Tuple["User", bool]:
        """python-telegram-bot's Update, Context --> User instance"""
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(
            user_id=data["user_id"], defaults=data
        )

        if created:
            u.is_blocked_bot = True
            u.comment = _("Новый пользователь")

        return u, created

    @classmethod
    def get_user(cls, update, context) -> "User":
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, string) -> Optional["User"]:
        """Search user in DB, return User or None if not found"""
        username = str(string).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @classmethod
    def find_users_by_keywords(cls, keywords) -> list:
        """осуществляет поиск участников, у которых в любом поле упоминаются ключевые слова"""
        q = (
            Q(username__icontains=keywords)
            | Q(last_name__icontains=keywords)
            | Q(first_name__icontains=keywords)
            | Q(patronymic__icontains=keywords)
            | Q(telefon__icontains=keywords)
            | Q(email__icontains=keywords)
            | Q(about__icontains=keywords)
            | Q(comment__icontains=keywords)
            | Q(sport__icontains=keywords)
            | Q(hobby__icontains=keywords)
        )
        users = cls.objects.filter(q).distinct()
        return users

    def short_profile(self) -> str:
        res = ""
        if self.username:
            res += f"<b>Логин телеграм:</b> @{mystr(self.username)}\n"
            full_name = " ".join(
                [
                    str(self.first_name),
                    # str(self.patronymic),
                    str(self.last_name),
                ]
            )
        res += f"<b>Имя:</b> {full_name}\n"
        return res

    def full_profile(self, language=DEFAULT_LANGUAGE) -> str:
        if language not in [i[0] for i in LANGUAGE]:
            language = DEFAULT_LANGUAGE
        with translation_override(language):
            res = "<b>" + _("Пользователь") + ":</b> \n"
            res += (
                f"@{self.username}\n"
                if self.username is not None
                else f"{self.user_id}\n"
            )
            res += " ".join(
                [
                    str(self.first_name),
                    # str(self.patronymic),
                    str(self.last_name),
                ]
            )
            # res += "\n<b>Личная информация:</b> "
            # res += "\n  <b>e-mail:</b> " + mystr(self.email)
            res += "\n<b>" + _("Телефон") + ":</b> " + mystr(self.telefon)
        return res

    def new_user_notification(self) -> str:
        res = "В группе новый участник\n"
        # res += f"@{mystr(self.username)}\n"
        res += f"{mystr(self.last_name)} {mystr(self.first_name)} {mystr(self.patronymic)}\n"
        return res

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
