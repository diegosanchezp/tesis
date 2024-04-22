from django import forms
from django_src.mentor.models import StudentMentorshipTask

class MentorshipTaskEventForm(forms.Form):

    event = forms.ChoiceField(
        choices=StudentMentorshipTask.Events.choices,
        widget=forms.HiddenInput(),
    )
