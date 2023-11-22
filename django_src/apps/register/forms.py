from django import forms
from django.contrib.auth.forms import BaseUserCreationForm
from django.contrib.auth import get_user_model
from django_src.apps.register.models import (
    Student, Carreer, InterestTheme, CarrerSpecialization
)
from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _

class StudentForm(forms.ModelForm):

    # Add an extra field for validating the selected profile
    profile = forms.ChoiceField(
        choices=[
            ("estudiante", _("Estudiante")),
            ("mentor", _("Mentor")),
            ("empresa",_("Empresa")),
        ],
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Student
        fields = ["interests", "specialization", "carreer", "voucher",]

        # https://docs.djangoproject.com/en/stable/topics/forms/modelforms#overriding-the-default-fields
        widgets = {
            # Many to many fields have to use MultipleHiddenInput, otherwise validation
            # error will be raised
            "interests": forms.MultipleHiddenInput(),
            "specialization": forms.HiddenInput(),
            "carreer": forms.HiddenInput(),
        }

        error_messages = {
            "specialization": {
                "invalid_choice": _(
                    "La especialización seleccionada no pertenece a la carrera seleccionada. "\
                    "Vuelve al paso 3, para corregir"
                )
            },
            "carreer": {
                "invalid_choice": _("La carrera seleccionada no existe. Vuelve al paso 2, para corregir"),
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
            self.add_error(field="interests", error="No se puede seleccionar temas de interés ya que tienes una especialización.")

        if not ( interests or specialization ):
            raise ValidationError(
                _("No haz seleccionado ni especialización ni tema de interés")
            )
        if interests:
            count_interests = carreer.interest_themes.filter(
                pk__in=list(interests.values_list("pk", flat=True))
            ).exists()

            if not count_interests:
                self.add_error(field="interests", error="No se puede seleccionar temas de interés que no pertenezca a la carrera seleccionada.")

        if specialization:
            count_specialization = carreer.carrerspecialization_set.filter(
                pk=specialization.pk
            ).exists()

            if not count_specialization:
                self.add_error(field="specialization", error="La especialización seleccionada no pertenece a la carrera seleccionada.")


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

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return

        if get_user_model().objects.filter(email=email).exists():
            raise ValidationError(
                _("Ya existe un usuario con este correo electrónico")
            )

        return email


    class Meta(BaseUserCreationForm.Meta):

        # https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.User
        model = get_user_model()
        fields = (
            "profile_pic", "first_name", "last_name", "email", "password1", "password2",
        )

        labels = {
            "profile_pic": "Añadir foto de perfil",
        }
