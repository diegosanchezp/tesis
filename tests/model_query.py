"""
Use the actual developement database to
test querys of the django model
"""
import unittest
from pathlib import Path

from shscripts.backup import (
    setup_django,
)

from django.apps import apps
from django.db.models import Prefetch

# python -m unittest tests.model_query.TestQuerys.
class TestQuerys(unittest.TestCase):

    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
        setup_django(self.BASE_DIR)

        app_label = "register"
        self.Faculty = apps.get_model(app_label, "Faculty")
        self.Carreer = apps.get_model(app_label, "Carreer")

        self.facultys = self.Faculty.objects.prefetch_related("carreers")
        self.ciencias = self.facultys.get(name="Ciencias")
        self.computacion = self.ciencias.carreers.get(name="Computación")

    # python -m unittest tests.model_query.TestQuerys.test_carreer_querys
    def test_carreer_querys(self):

        self.assertTrue(self.facultys.count() > 1)
        self.assertTrue(self.ciencias.carreers.count() > 1)
        print(self.computacion)

        # Get facultys that contains a carrer that is name com
        search_key="Compu"
        carreers = self.Faculty.objects.filter(carreers__name__icontains="Compu")
        self.assertEqual(carreers.count(), 1)

        # First get the carrers that matches the search key
        carreers = self.Carreer.objects.filter(name__icontains=search_key)

        # Then get the facultys of the carrers that matches
        facultys = self.Faculty.objects.filter(
            pk__in=carreers.values("faculty_id")
        ).prefetch_related(
            Prefetch(
                "carreers",
                # Istead of listing all the carreers, force to list those carreers
                # that matches the search_key
                queryset=carreers
            )
        )
        self.assertTrue(facultys.count(), 1)
        self.assertTrue(facultys[0].carreers.count(), 1)
        self.assertTrue(facultys[0].carreers.first() == self.computacion)
        breakpoint()

    # python -m unittest tests.model_query.TestQuerys.test_model_todict
    def test_model_todict(self):
        print(
            list(
                self.computacion.carrerspecialization_set.all().values("name")
            )
        )

