
import mimetypes

from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType

def get_file_type(voucher):
    """
    Returns the type of file for a voucher
    """

    # voucher.storage
    mime_type, _ = mimetypes.guess_type(voucher.name)
    if not mime_type:
        return

    if "image" in mime_type:
        return "image"

    _, extension = mime_type.split('/')
    if extension == "pdf":
        return extension

class RegisterApprovalStates(models.TextChoices):
    """
    Aproval States for an entity
    """

    # The inital state, Waiting for approval.
    WAITING = "WAITING", _("Esperando aprobación")

    # Student Approved
    APPROVED = "APPROVED", _("Aprobado")

    # Rejected
    REJECTED = "REJECTED", _("Rechazado")

class RegisterApprovalEvents(models.TextChoices):
    """
    Events that can happen in the approval process
    """
    REJECT = "REJECT", _("Rechazar")
    APPROVE = "APPROVE", _("Aprobar")

class RegisterApprovals(models.Model):

    # Generic relation for user that it is subject to approval or rejection
    # Can be of two types: Student or Mentor
    # user_id = models.PositiveIntegerField()
    user_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # user = GenericForeignKey("user_type", "user_id")
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="my_approvals",
    )
    # -----

    # An admin that approves, rejects, etc, the user
    admin = models.ForeignKey(
        verbose_name=_("Administrador"),
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="register_approvals",
        null=True,
        blank=True,
    )

    state = models.TextField(
        _("Estatus"),
        choices=RegisterApprovalStates.choices,
    )

    date = models.DateTimeField(
        verbose_name=_("Fecha"),
        auto_now=True,
    )

    class Meta:
        verbose_name = _("Aprobación de registro")
        verbose_name_plural = _("Aprobaciones de registro")

    def __str__(self) -> str:
        return f"{self.user} {self.user_type.model} {self.state} "

    @property
    def voucher(self):
        if self.user_type.model == "mentor":
            voucher = self.user.mentor.voucher
        elif self.user_type.model == "student":
            voucher = self.user.student.voucher
        else:
            return

        return voucher

    @property
    def voucher_file_type(self):
        if self.voucher:
            return get_file_type(self.voucher)



approval_state_machine = {
    RegisterApprovalStates.WAITING: {
        RegisterApprovalEvents.REJECT: RegisterApprovalStates.REJECTED,
        RegisterApprovalEvents.APPROVE: RegisterApprovalStates.APPROVED,
    },
    RegisterApprovalStates.REJECTED: {
        RegisterApprovalEvents.APPROVE: RegisterApprovalStates.APPROVED,
    }
}

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
        blank=True,
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

    voucher = models.FileField(
        upload_to="student_vouchers",
        verbose_name=_("Comprobante de estudios"),
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _("Estudiante")
        verbose_name_plural = _("Estudiantes")

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

    pro_carreers_match = GenericRelation(
        "ThemeSpecProCarreer",
        related_query_name="interest_theme",
        content_type_field="content_type",
        object_id_field="object_id",
    )

    def __str__(self) -> str:
        return f"{self.name}"

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

    voucher = models.FileField(
        upload_to="mentor_vouchers",
        verbose_name=_("Comprobante"),
        null=True,
        blank=True,
    )

    # the students to whom the mentor has mentored
    students = models.ManyToManyField(
        to="Student",
        verbose_name=_("Estudiantes mentoreados"),
        blank=True,
    )

    class Meta:
        verbose_name = _("Mentor")
        verbose_name_plural = _("Mentores")

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
        validators=[MinLengthValidator(4)],
    )

    company=models.TextField(
        verbose_name=_("Compañía"),
        validators=[MinLengthValidator(1)],
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
        validators=[MinLengthValidator(4)],
    )
    class Meta:
        verbose_name=_("Experiencia profesional")
        verbose_name_plural=_("Experiencias profesionales")
        unique_together = ["mentor", "name", "company", "init_year", "end_year"]

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

    interest_themes=models.ManyToManyField(
        to="InterestTheme",
        verbose_name=_("Temas de interés"),
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
        verbose_name=_("Carrer"),
        null=True,
        on_delete=models.CASCADE,
    )

    pro_carreers_match = GenericRelation(
        to="ThemeSpecProCarreer",
        related_query_name="carreer_specialization",
        content_type_field="content_type",
        object_id_field="object_id",

    )

    def __str__(self) -> str:
        return f"{self.name}"

class ThemeSpecProCarreer(models.Model):
    """
    A model that makes the relation between a Professional Carreer, a Theme Specification
    or Carreer Specialization
    """

    weight = models.PositiveIntegerField(default=0, blank=False, null=False)

    # For generic relationships
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    pro_career = models.ForeignKey(
        verbose_name=_("Carrera profesional"),
        to="pro_carreer.ProfessionalCarreer",
        on_delete=models.CASCADE,
        related_name="weighted_themespecs",
    )

    class Meta:
        unique_together = [["pro_career", "content_type", "object_id"]]

    def __str__(self) -> str:

        theme_type = ContentType.objects.get_for_model(InterestTheme)
        spec_type = ContentType.objects.get_for_model(CarrerSpecialization)

        object_str = ""

        if self.content_type == theme_type:

            object_str = self.content_object.name

        if self.content_type == spec_type:

            object_str = self.content_object.name

        return f"{self.pro_career.slug} weight={self.weight} {object_str}"
