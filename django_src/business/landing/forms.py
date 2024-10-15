from django import forms
from django_src.student.models import StudentJobOffer

class GetJobApplicationForm(forms.ModelForm):
    """
    Validates that the student has applied to the job offer
    """

    class Meta:
        model = StudentJobOffer
        fields = ["job", "student"]

