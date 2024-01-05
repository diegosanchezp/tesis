from django.test import TestCase

from .models import (
    Student,
    Mentor, MentorExperience,
    Faculty, Carreer,
    InterestTheme,
)

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
