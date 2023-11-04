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

    def test_carreer_querys(self):

        app_label = "register"
        Faculty = apps.get_model(app_label, "Faculty")
        Carreer = apps.get_model(app_label, "Carreer")
        facultys = Faculty.objects.prefetch_related("carreers")
        self.assertTrue(facultys.count() > 1)
        ciencias = facultys.get(name="Ciencias")
        self.assertTrue(ciencias.carreers.count() > 1)
        computacion = ciencias.carreers.get(name="Computación")
        print(computacion)

        # Get facultys that contains a carrer that is name com
        search_key="Compu"
        carreers = Faculty.objects.filter(carreers__name__icontains="Compu")
        self.assertEqual(carreers.count(), 1)

        # First get the carrers that matches the search key
        carreers = Carreer.objects.filter(name__icontains=search_key)

        # Then get the facultys of the carrers that matches
        facultys = Faculty.objects.filter(
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
        self.assertTrue(facultys[0].carreers.first() == computacion)
        breakpoint()

