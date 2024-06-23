from django import forms
from django_src.apps.register.models import Student, Carreer, CarrerSpecialization


class ChangeCareerForm(forms.Form):
    career = forms.ModelChoiceField(
        queryset=Carreer.objects.all(),
        to_field_name="name",
    )


class ChangeSpecializationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["specialization"].to_field_name = "name"
        self.fields["specialization"].required = False

    class Meta:
        model = Student
        fields = [
            "specialization",
        ]

    def clean(self):
        cleaned_data = super().clean()

        student = self.instance
        carreer = student.carreer

        if not carreer:
            return

        specialization = cleaned_data["specialization"]

        if specialization:
            count_specialization = carreer.carrerspecialization_set.filter(
                pk=specialization.pk
            ).exists()

            if not count_specialization:
                self.add_error(
                    field="specialization",
                    error="La especialización seleccionada no pertenece a la carrera seleccionada.",
                )
