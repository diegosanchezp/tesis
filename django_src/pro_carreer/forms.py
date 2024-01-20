from django_src.apps.register.models import (
    CarrerSpecialization, InterestTheme, ThemeSpecProCarreer
)

from django.db import models
from django.utils.translation import gettext_lazy as _


from django import forms

class BaseRelateForm(forms.Form):

    weight = forms.IntegerField(
        required=True,
        min_value=0,
    )

class RelateActions(models.TextChoices):
    RELATE_SPECIALIZATION = "relate_specialization", _("Relacionar especialización")
    DELETE_SPECIALIZATION = "delete_specialization", _("Eliminar especialización")
    RELATE_THEME = "relate_theme", _("Relacionar tema de interes")
    DELETE_THEME = "delete_theme", _("Eliminar tema de interes")

class ActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=RelateActions.choices,
    )

class SpecRelateForm(BaseRelateForm):
    """
    Form for relating specialization with professional career
    """

    specialization = forms.ModelChoiceField(
        queryset=CarrerSpecialization.objects.all()
    )

class DeleteSpecRelateForm(forms.Form):

    specialization = forms.ModelChoiceField(
        queryset=CarrerSpecialization.objects.all()
    )
    weighted_spec = forms.ModelChoiceField(
        queryset=ThemeSpecProCarreer.objects.all()
    )

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data:
            return

        specialization = cleaned_data.get("specialization")
        weighted_spec = cleaned_data.get("weighted_spec")

        if not weighted_spec and not specialization:
            return cleaned_data

        # Check that the specialization 
        if weighted_spec.content_object != specialization:
            raise forms.ValidationError(
                _("La especialización no pertenece a este peso")
            )


class ThemeRelateForm(BaseRelateForm):
    """
    Form for relating interest themes with professional career
    """

    theme = forms.ModelChoiceField(
        queryset=InterestTheme.objects.all()
    )

