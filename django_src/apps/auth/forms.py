from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserProfileForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["profile_pic"].required = False
        self.fields["profile_pic"].widget.attrs.update(form="profile-form")
        self.fields["first_name"].required = True
        self.fields["last_name"].required = True
        self.fields["email"].required = True

    class Meta:
        # https://docs.djangoproject.com/en/stable/ref/contrib/auth/#django.contrib.auth.models.User
        model = User
        fields = (
            "profile_pic",
            "first_name",
            "last_name",
            "email",
        )
        labels = {
            "profile_pic": "Añadir o cambiar Foto de perfil",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email:
            return

        # Do not validate if the email is the same
        if email == self.instance.email:
            return email

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico"))

        return email
