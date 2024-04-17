from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django_src.apps.register.models import (
    RegisterApprovals,
)

from .models import (
    Student,
    Mentor, MentorExperience,
    Faculty, Carreer,
    InterestTheme,
)
from .test_data.students import StudentData

class TestCaseWithData(TestCase):
    """
    Injects models to the test case
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.faculty, created = Faculty.objects.get_or_create(
            name="Ciencias",
        )

        cls.User = get_user_model()

        cls.admin_user = cls.User.objects.get(
            username=settings.ADMIN_USERNAME,
        )

        cls.computacion, created = cls.faculty.carreers.get_or_create(name="Computación")
        cls.matematicas, created = cls.faculty.carreers.get_or_create(name="Matemáticas")

        cls.computacion_interests = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Matemáticas"),
                InterestTheme(name="Programación"),
            ]
        )

        cls.mates_interest_set = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Cálculo"),
                InterestTheme(name="Límites"),
            ]
        )

        cls.ati, created = cls.computacion.carrerspecialization_set.get_or_create(
            name="Aplicaciones Tecnología Internet",
        )

        cls.elementos, created = cls.matematicas.carrerspecialization_set.get_or_create(
            name="Elementos",
        )

        cls.computacion.interest_themes.add(*cls.computacion_interests)
        cls.matematicas.interest_themes.add(*cls.mates_interest_set)

        cls.student_data = StudentData()
        cls.student_data.create()

        cls.student_user = cls.student_data.student_user
        cls.student = cls.student_data.student
        cls.student_approval = cls.student_data.student_approval

        cls.unapproved_student_user = cls.student_data.unapproved_student_user
        cls.unapproved_student = cls.student_data.unapproved_student
        cls.unapproved_student_approval = cls.student_data.unapproved_student_approval

        cls.mentor_user = cls.User.objects.create(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
        )
        cls.mentor_user.set_password("dev123456")
        cls.mentor_user.save()
