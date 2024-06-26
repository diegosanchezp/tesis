from django import forms
from django_src.apps.register.forms import MentorExperienceForm, validateExperienceFormset
from django_src.apps.register.models import Mentor, MentorExperience


class MentorExperienceBaseFormSet(forms.BaseInlineFormSet):

    def clean(self):
        """
        Check that no two experiences have the same name.
        """
        super().clean()
        validateExperienceFormset(self)


def get_MentorExperienceFormSet(extra=0):
    MentorExperienceFormSet = forms.inlineformset_factory(
        parent_model=Mentor,
        model=MentorExperience,
        form=MentorExperienceForm,
        formset=MentorExperienceBaseFormSet,
        extra=extra,
        max_num=50,
        exclude=["id", "mentor"],
        can_delete_extra=True,
    )
    return MentorExperienceFormSet
