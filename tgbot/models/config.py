from django.db import models
from typing import Dict
from django.utils.translation import gettext_lazy as _


class Config(models.Model):
    """Модель настроек бота."""

    param_name = models.CharField(_('Наименование параметра'), max_length=255)
    param_val = models.TextField(_('Значение параметра'), null=True, blank=True)

    def __str__(self):
        return self.param_name

    class Meta:
        ordering = ['param_name']
        verbose_name = _('Параметр бота')
        verbose_name_plural = _('Параметры бота')

    @classmethod
    def load_config(cls) -> Dict[str, str]:
        config_params = cls.objects.all()
        result = {}
        for config_param in config_params:
            result[config_param.param_name] = config_param.param_val

        return result