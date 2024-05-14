from django.urls import reverse
from django.conf import settings

class GetUrlModelMixin:
    def get_admin_url(self):
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.pk,))

    def get_url(self):
        domain = settings.DOMAIN
        if settings.DEBUG:
            domain = 'http://0.0.0.0:8000'
        return domain + self.get_admin_url()