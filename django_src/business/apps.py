from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BusinessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Negocio")
    name = "django_src.business"
    label = "business"
