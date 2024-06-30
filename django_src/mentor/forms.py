from django.forms import modelformset_factory
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Mentorship, MentorshipTask, MentorshipRequest
from django.forms import ModelForm


class MentorshipForm(ModelForm):
    class Meta:
        model = Mentorship
        fields = ["name", "mentor"]

        widgets = {"mentor": forms.HiddenInput()}


def get_MentorshipTaskFormSet(extra: int = 1, max_num: int | None = None):
    return modelformset_factory(
        model=MentorshipTask,
        exclude=["mentorship"],
        extra=extra,
        max_num=max_num,
    )


MentorshipTaskFormSet = get_MentorshipTaskFormSet()


class MentorshipRequestActionForm(forms.Form):

    action = forms.ChoiceField(
        choices=MentorshipRequest.Events.choices,
        widget=forms.HiddenInput(),
    )
    with_mentorship_name = forms.BooleanField(required=False, widget=forms.HiddenInput())


class MentorshipReqFilterForm(forms.Form):
    state = forms.ChoiceField(
        choices=[("", "Ninguno")] + list(MentorshipRequest.State.choices),
        label=_("Estatus"),
        required=False,
    )

    student_name = forms.CharField(
        label=_("Estudiante"),
        required=False,
    )

    student_name.widget.attrs.update(
        {
            "placeholder": "Nombre del estudiante",
        },
    )
