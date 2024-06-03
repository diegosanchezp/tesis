from django import forms
from django_src.apps.register.models import Carreer, InterestTheme, CarrerSpecialization
from django.utils.translation import gettext_lazy as _
from django.db import models


def get_carreer_field(required=False):
    carreer_field = forms.ModelChoiceField(
        label=_("Carrera"),
        queryset=Carreer.objects.order_by("name"),
        to_field_name="name",
        required=required,
    )

    return carreer_field


class FilterForm(forms.Form):
    career = get_carreer_field()
    # Student filters
    name_last_name = forms.CharField(required=False, label=_("Nombre y Apellido"))
    email = forms.EmailField(required=False, label="E-mail")
    interests = forms.ModelMultipleChoiceField(
        label=_("Intereses"),
        queryset=InterestTheme.objects.all(),
        to_field_name="name",
        required=False,
    )

    specialization = forms.ModelChoiceField(
        label=_("Especialización"),
        queryset=CarrerSpecialization.objects.all(),
        to_field_name="name",
        required=False,
    )


class Actions(models.TextChoices):
    FILTER_PAGINATE_STUDENTS = "filter_paginate_students", _(
        "Paginar y Filtrar Estudiantes"
    )
    RENDER_INTERESTS = "render_interests", _("Renderizar Intereses")
    FILTER_STUDENTS = "filter_students", _("Filtrar Estudiantes")


class ActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=Actions.choices,
        required=True,
    )


class PaginationForm(forms.Form):
    """
    For paginating the students of a carreer
    """

    carreer = get_carreer_field(required=True)
    page = forms.IntegerField(min_value=1, required=True)  # page_number
