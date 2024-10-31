from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Professor(models.Model):
    """
    The Professor model
    """

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professor",
    )

    class Meta:
        verbose_name = _("Profesor")
        verbose_name_plural = _("Profesores")
