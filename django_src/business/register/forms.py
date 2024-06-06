from django import forms
from django_src.business.models import Business
from django_src.apps.register.forms import UserCreationForm
from django.contrib.auth.forms import BaseUserCreationForm
from django.db import models


class BusinessForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Alpine attributes
        # x-model is used to bind the field to Alpine.js which saves it to localStorage
        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "x-model": field_name,
                }
            )

    class Meta:
        model = Business
        fields = ["description", "web_page"]
        help_texts = {
            "web_page": "La pagina web se utilizará para verificar la autenticidad de la empresa",
        }
        labels = {
            "description": "Descripción de la empresa",
            "web_page": "Página web de la empresa",
        }


class BusinessUserCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        # Don't call the UserCreationForm __init__ method because it uses the last_name field
        BaseUserCreationForm.__init__(self, *args, **kwargs)

        # Especificar que el first_name y last_name sean requeridos
        self.fields["first_name"].required = True

        # Profile pic is not enforced
        self.fields["profile_pic"].required = False

        # Add Alpine attributes
        # x-model is used to bind the field to Alpine.js which saves it to localStorage
        for field_name, field in self.fields.items():

            field.widget.attrs.update(
                {
                    "x-model": field_name,
                }
            )

    class Meta(UserCreationForm.Meta):
        labels = {
            "profile_pic": "Logo de la empresa (opcional)",
            "first_name": "Nombre de la empresa",
        }
        exclude = ["last_name"]

        fields = (
            "first_name",
            "email",
            "profile_pic",
            "password1",
            "password2",
        )


class BusinessRegisterAction(models.TextChoices):
    REGISTER = "register"


class ActionForm(forms.Form):
    action = forms.ChoiceField(choices=BusinessRegisterAction.choices, required=True)
