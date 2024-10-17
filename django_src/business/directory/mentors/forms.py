from django import forms
from django_src.apps.register.models import Carreer
from django.utils.translation import gettext_lazy as _
from django.db import models

class MentorFilterForm(forms.Form):
    name_last_name = forms.CharField(required=False, label=_("Nombre y Apellido"))
    email = forms.EmailField(required=False, label="E-mail")
    career = forms.ModelChoiceField(
        label=_("Carrera"),
        queryset=Carreer.objects.order_by("-name"),
        to_field_name="name",
        required=False,
    )

class Actions(models.TextChoices):
    FILTER_MENTORS = "filter_mentors", _("Filtrar Mentores")

class ActionForm(forms.Form):
    action = forms.ChoiceField(
        choices=Actions.choices,
        required=True,
    )
