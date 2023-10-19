from django.db import models
from django.conf import settings

from django.utils.translation import gettext_lazy as _

# Create your models here.
class Student(models.Model):
    """
    Student Model
    """

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student",
    )

    interests=models.ManyToManyField(
        to="InterestTheme",
        verbose_name=_("Intereses"),
        through="StudentInterest",
        through_fields=("student","interest"),
    )

    specialization=models.ForeignKey(
        to="CarrerSpecialization",
        null=True,
        verbose_name=_("Especialización"),
        on_delete=models.SET_NULL,
        related_name="students",
    )

    carreer=models.ForeignKey(
        to="Carreer",
        verbose_name=_("Carrera"),
        on_delete=models.CASCADE,
        related_name="students",

    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

class StudentInterest(models.Model):
    """
    Many to many between student and interest
    """

    interest=models.ForeignKey(
        to="InterestTheme",
        verbose_name=_("Tema de interés"),
        on_delete=models.CASCADE,
    )

    student=models.ForeignKey(
        to="Student",
        verbose_name=_("Estudiante"),
        on_delete=models.CASCADE,
    )


class InterestTheme(models.Model):
    """
    The student theme interests
    """
    name=models.TextField(
        verbose_name=_("Nombre"),
    )

class Mentor(models.Model):
    """
    The Mentor model
    """

    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mentor",
    )

    carreer=models.ForeignKey(
        to="Carreer",
        verbose_name=_("Carrera"),
        on_delete=models.CASCADE,
        related_name="mentors",

    )

    # the students to whom the mentor has mentored
    students = models.ManyToManyField(
        to="Student",
        verbose_name=_("Estudiantes mentoreados")
    )

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

class MentorExperience(models.Model):
    """
    Professional market experiencie of the mentor
    """
    mentor = models.ForeignKey(
        to="Mentor",
        on_delete=models.CASCADE,
        related_name="experiences",
        verbose_name=_("Experiencie Mentor"),
    )

    name=models.TextField(
        verbose_name=_("Nombre del cargo"),
        help_text=_("Ej: Frontend developer"),
    )

    company=models.TextField(
        verbose_name=_("Compañía"),
    )

    init_year=models.DateField(
        verbose_name=_("Año inicio"),
    )

    end_year=models.DateField(
        verbose_name=_("Año fin"),
        null=True,
        blank=True,
    )

    current=models.BooleanField(
        verbose_name=_("¿ Cargo actual ?"),
    )

    description = models.TextField(
        verbose_name=_("Descripción del cargo"),
    )

    def __str__(self) -> str:
        return f"{self.name}, {self.company}"

class Faculty(models.Model):
    """
    Faculty entity
    """
    name = models.TextField(_("Nombre"), unique=True)

    def __str__(self) -> str:
        return f"{self.name}"

class Carreer(models.Model):
    """
    Carreer entity
    """

    name = models.TextField(_("Nombre"), unique=True)
    faculty=models.ForeignKey(
        to="Faculty",
        null=True,
        verbose_name=_("faculty"),
        on_delete=models.SET_NULL,
        related_name="carreers",
    )

    def __str__(self) -> str:
        return f"{self.name}"

class CarrerSpecialization(models.Model):
    """
    The especialization of the carreer
    """
    name = models.TextField(_("Nombre"), unique=True)
    career=models.ForeignKey(
        to="Carreer",
        verbose_name=_("faculty"),
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self) -> str:
        return f"{self.name}"
