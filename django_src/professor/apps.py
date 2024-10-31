from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProfessorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_src.professor"
    verbose_name = _("Profesor")
    label = "professor"
