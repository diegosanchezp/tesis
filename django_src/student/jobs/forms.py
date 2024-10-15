from django import forms
from django_src.apps.register.models import Student
from django_src.business.models import JobOffer
from django_src.student.models import StudentJobOffer
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ApplyForm(forms.Form):
    job = forms.ModelChoiceField(queryset=JobOffer.objects.all())

class UnApplyForm(forms.Form):
    job_application: StudentJobOffer
    job_offer = forms.ModelChoiceField(queryset=JobOffer.objects.all())

    def __init__(self, student: Student ,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student

    def clean_job_offer(self):
        job_offer: JobOffer = self.cleaned_data["job_offer"]
        try:
            self.job_application = StudentJobOffer.objects.get(student=self.student, job=job_offer)
        except StudentJobOffer.DoesNotExist:
            raise ValidationError(_("No haz mostrado interes por esta oferta de trabajo"))
        return job_offer

class JobSearchForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].required = False
    class Meta:
        model = JobOffer
        labels = {
            "title": "Buscar por título"
        }
        help_texts = {
            "title": "",
        }
        fields = [
            "title",
        ]
