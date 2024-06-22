from django import forms
from django_src.apps.register.models import Student, Carreer, CarrerSpecialization


class ChangeCareerForm(forms.Form):
    career = forms.ModelChoiceField(
        queryset=Carreer.objects.all(),
        to_field_name="name",
    )


class ChangeSpecializationForm(forms.Form):
    # TODO: add in the constructor a filter by career
    specialization = forms.ModelChoiceField(
        queryset=CarrerSpecialization.objects.all(),
        to_field_name="name",
    )


class EditStudentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Enforce the fields to be required
        self.fields["specialization"].required = False
        self.fields["interests"].required = False
        self.fields["carreer"].to_field_name = "name"
        self.fields["specialization"].to_field_name = "name"
        self.fields["interests"].to_field_name = "name"

    class Meta:

        model = Student
        fields = [
            "interests",
            "specialization",
            "carreer",
        ]

        # https://docs.djangoproject.com/en/stable/topics/forms/modelforms#overriding-the-default-fields
        widgets = {
            # Many to many fields have to use MultipleHiddenInput, otherwise validation
            # error will be raised
            "interests": forms.MultipleHiddenInput(),
            "specialization": forms.HiddenInput(),
            "carreer": forms.HiddenInput(),
        }
