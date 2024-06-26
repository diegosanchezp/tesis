from datetime import date
from django import forms
from django.db.models import Q, TextChoices
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models.query import QuerySet
from django_src.settings.widget import DATE_INPUT_FORMAT

from django_src.apps.register.models import (
    Carreer,
    Mentor,
    Student,
    MentorExperience,
    RegisterApprovals,
    RegisterApprovalStates,
    RegisterApprovalEvents,
    approval_state_machine,
)

from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _


class QueryForm(forms.Form):
    """
    Validates the query paramters of the view
    """

    ESTUDIANTE = "estudiante"
    MENTOR = "mentor"
    EMPRESA = "empresa"

    profile = forms.ChoiceField(
        choices=[
            (ESTUDIANTE, _("Estudiante")),
            (MENTOR, _("Mentor")),
            (EMPRESA, _("Empresa")),
        ],
        widget=forms.HiddenInput(),
        required=True,
    )

    carreer = forms.ModelChoiceField(
        required=True,
        queryset=Carreer.objects.all(),
        to_field_name="name",
        widget=forms.HiddenInput(),
    )


class StudentForm(forms.ModelForm):

    # Add an extra field for validating the selected profile
    profile = forms.ChoiceField(
        choices=[
            (QueryForm.ESTUDIANTE, _("Estudiante")),
        ],
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Student
        fields = [
            "interests",
            "specialization",
            "carreer",
            "voucher",
        ]

        # https://docs.djangoproject.com/en/stable/topics/forms/modelforms#overriding-the-default-fields
        widgets = {
            # Many to many fields have to use MultipleHiddenInput, otherwise validation
            # error will be raised
            "interests": forms.MultipleHiddenInput(),
            "specialization": forms.HiddenInput(),
            "carreer": forms.HiddenInput(),
        }
        help_texts = {
            "voucher": _(
                "Puedes utilizar tu carnet, kardex, o cualquier documento que compruebe que eres estudiante de la UCV."
            ),
        }

        error_messages = {
            "specialization": {
                "invalid_choice": _(
                    "La especialización seleccionada no pertenece a la carrera seleccionada. "
                    "Vuelve al paso 3, para corregir"
                )
            },
            "carreer": {
                "invalid_choice": _(
                    "La carrera seleccionada no existe. Vuelve al paso 2, para corregir"
                ),
            },
            # "interests": {
            #
            # },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce the fields to be required
        self.fields["voucher"].required = True
        self.fields["specialization"].required = False
        self.fields["interests"].required = False
        self.fields["carreer"].to_field_name = "name"
        self.fields["specialization"].to_field_name = "name"
        self.fields["interests"].to_field_name = "name"
        self.fields["voucher"].widget.attrs.update(form="abc-form")

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data:
            return

        carreer = cleaned_data.get("carreer")

        # The two fields below, depend on the carreer
        interests = cleaned_data.get("interests")
        specialization = cleaned_data.get("specialization")

        if not carreer:
            return

        if interests and specialization:
            self.add_error(
                field="interests",
                error="No se puede seleccionar temas de interés ya que tienes una especialización.",
            )

        if not (interests or specialization):
            raise ValidationError(
                _("No haz seleccionado ni especialización ni tema de interés")
            )
        if interests:
            count_interests = carreer.interest_themes.filter(
                pk__in=list(interests.values_list("pk", flat=True))
            ).exists()

            if not count_interests:
                self.add_error(
                    field="interests",
                    error="No se puede seleccionar temas de interés que no pertenezca a la carrera seleccionada.",
                )

        if specialization:
            count_specialization = carreer.carrerspecialization_set.filter(
                pk=specialization.pk
            ).exists()

            if not count_specialization:
                self.add_error(
                    field="specialization",
                    error="La especialización seleccionada no pertenece a la carrera seleccionada.",
                )


class UserCreationForm(BaseUserCreationForm):
    """
    Customized user form for registration of student or mentor
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Especificar que el first_name y last_name sean requeridos
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True

        # Profile pic is not enforced
        self.fields["profile_pic"].required = False
        self.fields["email"].required = True
        self.fields["email"].widget.attrs.update(
            {"placeholder": "diego@mail.com", "autocomplete": "email"}
        )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return

        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico"))

        return email

    class Meta(BaseUserCreationForm.Meta):

        # https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.User
        model = get_user_model()
        fields = (
            "profile_pic",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

        labels = {
            "profile_pic": "Añadir foto de perfil",
        }


class MentorExperienceForm(forms.ModelForm):
    today: date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.today = date.today()

        self.fields["name"].min_length = 4
        self.fields["name"].required = True
        self.fields["company"].min_length = 1
        self.fields["company"].required = True
        self.fields["description"].min_length = 4
        self.fields["description"].required = True

    class Meta:
        model = MentorExperience
        widgets = {
            "name": forms.TextInput(attrs={"required": True, "minlength": 4}),
            "company": forms.TextInput(attrs={"required": True, "minlength": 1}),
            "description": forms.Textarea(
                attrs={"rows": 3, "required": True, "minlength": 4}
            ),
            "init_year": forms.DateInput(
                format=DATE_INPUT_FORMAT, attrs={"type": "date", "required": True}
            ),
            "end_year": forms.DateInput(
                format=DATE_INPUT_FORMAT, attrs={"type": "date"}
            ),
        }
        help_texts = {
            "name": _("Ej: Frontend developer"),
        }

        exclude = ["mentor", "id", "pk"]

    def clean(self):

        cleaned_data = super().clean()
        if not cleaned_data:
            return cleaned_data

        current = cleaned_data.get("current")
        end_year = cleaned_data.get("end_year")
        init_year = cleaned_data.get("init_year")

        if not current and not end_year:
            self.add_error(
                field="current",
                error=_(
                    "Marca si este cargo es el actual, o añade el año de finalización"
                ),
            )

        if init_year:
            if init_year > self.today:
                self.add_error(
                    field="init_year",
                    error=_("El año de inicio no puede ser mayor al año actual"),
                )

        # End year can be
        return cleaned_data


def validateExperienceFormset(formset: forms.BaseModelFormSet):

    if any(formset.errors):
        # Don't bother validating the formset unless each form is valid on its own
        return

    actual_exp_count = 0

    for form in formset.forms:
        if formset.can_delete and formset._should_delete_form(form):
            continue
        # experience = form.cleaned_data["name"]

        current = form.cleaned_data.get("current")
        if current:
            actual_exp_count += 1
        if actual_exp_count > 3:
            raise ValidationError(
                _("No se puede tener más de tres cargos actuales")
            )

class MentorExperienceBaseFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = MentorExperience.objects.none()

    def clean(self):
        """
        Check that no two experiences have the same name.
        """
        super().clean()
        validateExperienceFormset(self)



def get_MentorExperienceFormSet(extra: int = 1, max_num: int | None = None):

    MentorExperienceFormSet = forms.modelformset_factory(
        MentorExperience,
        formset=MentorExperienceBaseFormSet,
        form=MentorExperienceForm,
        extra=extra,
        max_num=max_num,
        exclude=["id", "mentor"],
    )
    return MentorExperienceFormSet


class MentorForm(forms.ModelForm):

    profile = forms.ChoiceField(
        choices=[
            (QueryForm.MENTOR, _("Mentor")),
        ],
        widget=forms.HiddenInput(),
        required=True,
    )

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.fields["voucher"].required = True
        self.fields["carreer"].to_field_name = "name"
        self.fields["voucher"].widget.attrs.update(form="abc-form")

    class Meta:
        model = Mentor
        fields = (
            "carreer",
            "voucher",
        )
        help_texts = {
            "voucher": _(
                "Puedes utilizar tu carnet, kardex, o cualquier documento que compruebe que fuiste estudiante de la UCV."
            ),
        }

        # https://docs.djangoproject.com/en/stable/topics/forms/modelforms#overriding-the-default-fields
        widgets = {"carreer": forms.HiddenInput()}


class UserTypeChoiceField(forms.ModelChoiceField):
    """
    Just to get a better name for the options of this field
    """

    def label_from_instance(self, obj: ContentType):
        return obj.name


class ApprovalModalitys(TextChoices):
    """
    UI ways to approve or reject a request
    """

    # A single Approval is being approved or rejected in a modal
    MODAL = "modal", _("Modal")
    # One or More Approvals are being approved or rejected from the table
    TABLE = "table", _("Tabla")


class ApprovalsFilterForm(forms.Form):

    # --- Filters ---
    name = forms.CharField(
        label=_("Nombre"),
        strip=True,
        required=False,
    )

    status = forms.ChoiceField(
        label=_("Estatus"),
        choices=[("all", _("Todos"))] + RegisterApprovalStates.choices,
        required=False,
    )

    action = forms.ChoiceField(
        label=_("Acciones"),
        choices=RegisterApprovalEvents.choices + [("search", _("Buscar"))],
        required=True,
    )

    modality = forms.ChoiceField(
        choices=ApprovalModalitys.choices,
    )

    user_type = UserTypeChoiceField(
        label=_("Tipo"),
        queryset=ContentType.objects.filter(
            model__in=["mentor", "student", "business"]
        ),
        to_field_name="model",
        empty_label=_("Todos"),
        required=False,
    )

    # --- End Filters ---
    approvals = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, *args, approvals=None, **kwargs):
        super().__init__(*args, **kwargs)

        # This field is not rendered
        if approvals is None:
            # Users that are in the approval request table
            approvals = RegisterApprovals.objects.all()

        self.initial["status"] = "all"
        self.fields["approvals"].queryset = approvals

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data:
            return cleaned_data

        # Validate that the action is valid for the current state

        approvals: QuerySet[RegisterApprovals] | None = cleaned_data.get("approvals")
        action: RegisterApprovalEvents | None = cleaned_data.get("action")

        if not action:
            return cleaned_data

        approval_errors = []

        if action in [RegisterApprovalEvents.APPROVE, RegisterApprovalEvents.REJECT]:

            if not approvals:
                return cleaned_data

            for approval in approvals:

                try:
                    approval_state_machine[approval.state][action]
                except KeyError:
                    # If there is no next state, it means that the action is not valid for the current state
                    approval_errors.append(
                        ValidationError(
                            _(
                                "Acción %(accion)s, es inválida para el estado %(state)s de %(user)s"
                            ),
                            params={
                                "accion": RegisterApprovalEvents[action].label,
                                "state": RegisterApprovalStates[approval.state].label,
                                "user": f"{approval.user.first_name} {approval.user.last_name}",
                            },
                            code="invalid_action",
                        )
                    )

            # Raise the errors if any
            if len(approval_errors) > 0:
                raise ValidationError(approval_errors)
