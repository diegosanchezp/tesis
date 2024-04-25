from django.db import models
from django.contrib.auth.models import AbstractUser
from django_src.apps.register.models import Mentor, Student
# If you’re starting a new project, it’s highly recommended to set up a custom user model, even if the default User model is sufficient for you
# https://docs.djangoproject.com/en/stable/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

class User(AbstractUser):
    profile_pic = models.ImageField(
        upload_to="profile_pics",
        null=True,
        blank=False,
    )

    @property
    def is_mentor(self):
        mentor_queryset = Mentor.objects.filter(user=self)
        is_mentor = mentor_queryset.exists()
        return is_mentor

    @property
    def is_student(self):
        student_queryset = Student.objects.filter(user=self)
        is_student = student_queryset.exists()
        return is_student
