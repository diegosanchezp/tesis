from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.

class StudentJobOffer(models.Model):
    """
    Many to many between student and interest
    """

    job = models.ForeignKey(
        to="business.JobOffer",
        verbose_name=_("Oferta de Trabajo"),
        on_delete=models.CASCADE,
    )

    student = models.ForeignKey(
        to="register.Student",
        verbose_name=_("Estudiante"),
        on_delete=models.CASCADE,
    )

    # When the student applied
    date = models.DateTimeField(
        verbose_name=_("Fecha de aplicación"),
        auto_now_add=True,
    )
    def __str__(self) -> str:
        return f"{self.student.user.username} {self.job.title}"
