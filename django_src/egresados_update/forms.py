from django import forms
from django.db import models
from .models import EgresadosData
from django.utils.translation import gettext_lazy as _
from django_src.settings.widget import DATE_INPUT_FORMAT


class EgresadosUpdateForm(forms.ModelForm):
    class Meta:
        model = EgresadosData
        exclude = ["estatus", "cedula", "prefijo_cedula"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['cedula'].disabled = True
        # self.fields['prefijo_cedula'].disabled = True

        # Update date fields to use forms.DateInput widget
        for field_name, field in self.fields.items():
            if isinstance(field, forms.DateField):
                # Preserve any existing widget attributes
                original_attrs = (
                    field.widget.attrs.copy() if hasattr(field.widget, "attrs") else {}
                )
                original_attrs.update({"type": "date"})

                self.fields[field_name].widget = forms.DateInput(
                    attrs=original_attrs, format=DATE_INPUT_FORMAT
                )


class EgresadoUpdateValidate(forms.Form):
    pk = forms.ModelChoiceField(
        to_field_name="pk",
        queryset=EgresadosData.objects.all(),
    )

    prefijo_cedula = forms.ChoiceField(
        choices=EgresadosData.PrefijoCedula.choices,
    )

    cedula = forms.IntegerField(
        min_value=0,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):

        cleaned_data = super().clean()

        if not cleaned_data:
            return
        instance = cleaned_data["pk"]
        prefijo_cedula = cleaned_data["prefijo_cedula"]
        cedula = cleaned_data["cedula"]

        if prefijo_cedula != instance.prefijo_cedula or cedula != instance.cedula:
            raise ValueError(_("El id enviado no coincide con la cédula y nombre"))
        self.instance = instance


class CedulaForm(forms.Form):
    prefijo_cedula = forms.ChoiceField(
        label=_("Prefijo cédula"),
        choices=EgresadosData.PrefijoCedula.choices,
    )
    cedula = forms.IntegerField(
        label=_("Cédula"),
        min_value=0,
    )
    # class Meta:
    #     model = EgresadosData
    #     fields = ["prefijo_cedula", "cedula"]


class GETActionTypes(models.TextChoices):
    CONSULTAR = "CONSULTAR", _("Consultar")


class GETActionTypesForm(forms.Form):

    action = forms.ChoiceField(
        choices=GETActionTypes.choices,
        required=True,
        widget=forms.HiddenInput(),
    )
