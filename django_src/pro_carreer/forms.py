from django_src.apps.register.models import (
    CarrerSpecialization, InterestTheme, ThemeSpecProCarreer
)

from django.db import models
from django.utils.translation import gettext_lazy as _


from django import forms

# class BaseRelateForm(forms.Form):
#
#     weight = forms.IntegerField(
#         required=True,
#         min_value=0,
#     )

class RelateActions(models.TextChoices):
    RELATE_THEME_SPEC = "relate_specialization", _("Relacionar")
    DELETE_THEME_SPEC = "delete_specialization", _("Eliminar")

class ActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=RelateActions.choices,
        widget=forms.HiddenInput,
    )

    model_type = forms.ChoiceField(
        choices=[
            (CarrerSpecialization.__name__,CarrerSpecialization.__name__),
            (InterestTheme.__name__,InterestTheme.__name__),
        ],
        widget=forms.HiddenInput,
    )

class ThemeSpecRelateForm(forms.Form):
    """
    Form for relating specialization with professional career
    """

    weight = forms.IntegerField(
        required=True,
        min_value=0,
    )

    # Can be of type theme of spec
    theme_spec = forms.ModelChoiceField(
        queryset=None,
    )

    model_type: str

    def __init__(self, model: type[CarrerSpecialization] | type[InterestTheme], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = model.__name__
        self.fields["theme_spec"].queryset = model.objects.all()


class DeleteThemeSpecRelateForm(forms.Form):

    theme_spec = forms.ModelChoiceField(
        queryset=CarrerSpecialization.objects.all()
    )

    weighted_spec = forms.ModelChoiceField(
        queryset=ThemeSpecProCarreer.objects.all()
    )

    model_type: str

    def __init__(self, model: type[CarrerSpecialization] | type[InterestTheme], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_type = model.__name__
        self.fields["theme_spec"].queryset = model.objects.all()

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data:
            return

        specialization = cleaned_data.get("theme_spec")
        weighted_spec = cleaned_data.get("weighted_spec")

        if not weighted_spec and not specialization:
            return cleaned_data

        # Check that the specialization 
        if weighted_spec.content_object != specialization:
            raise forms.ValidationError(
                _("La especialización no pertenece a este peso")
            )
