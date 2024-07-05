from django import forms

from django_src.apps.register.models import InterestTheme


class TableFilterForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = "interest-filter-form"
        self.fields["name"].widget = forms.TextInput(
            attrs={"minlength": 1, "placeholder": "Nombre ..."}
        )
        self.fields["name"].required = False
        self.fields["name"].label = "Buscar por nombre"

    class Meta:
        model = InterestTheme
        fields = [
            "name",
        ]


class EditInterestThemeForm(forms.ModelForm):
    def __init__(self, form_id: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance_id = self.instance.id if self.instance.id else ""
        self.id = f"{form_id}{instance_id}"
        self.fields["name"].widget = forms.TextInput(
            attrs={"required": True, "minlength": 1, "form": self.id}
        )

    class Meta:
        model = InterestTheme
        fields = [
            "name",
        ]
