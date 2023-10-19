from django.db import models
from django.contrib.auth.models import AbstractUser

# If you’re starting a new project, it’s highly recommended to set up a custom user model, even if the default User model is sufficient for you
# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

class User(AbstractUser):
    profile_pic = models.ImageField(
        upload_to="profile_pics",
        null=True,
        blank=False,
    )
