from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ShedulerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "sheduler"
    verbose_name = _("Планировщик")
    
