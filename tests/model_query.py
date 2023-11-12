"""
Use the actual developement database to
test querys of the django model
"""
import unittest
from pathlib import Path
from django.core.paginator import Paginator
from django.db.models import Q, Value, Case, When

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
    # python -m unittest tests.model_query.TestQuerys.test_themes_pagination
    def test_themes_pagination(self):
        """
        Please se the view version of this test in

        django_src.apps.register.tests.InterestThemeViewTest.get_with_themes
        """
        interest_themes = self.computacion.interest_themes.all()
        selected_themes_list=["Programación","Matemáticas","BPM"]

        # Make the order
        order = [
            When(name=theme, then=Value(idx))
            for idx,theme in enumerate(selected_themes_list)
        ]

        self.assertEqual(len(order), len(selected_themes_list))

        selected_themes = interest_themes.filter(name__in=selected_themes_list).annotate(
            # Add metadata column to know that the value is selected
            selected=Value(True),
            # Add metadata column to keep the original order
            relevancy=Case(
                *order,
            ),
        )

        # Query set should have the same length
        self.assertEqual(selected_themes.count(), len(selected_themes_list))

        # Check if selected attribute was set, otherwise throws exception
        print(selected_themes.first().selected)

        # Query set should have the same items
        for theme in selected_themes.values("name"):
            self.assertIn(theme["name"], selected_themes_list)

        rest_of_themes = interest_themes.filter(~Q(name__in=selected_themes_list)).annotate(
            # Add metadata column to know if 
            selected=Value(False),
            relevancy=Value(len(selected_themes_list) + 1)
        )

        # Check if selected attribute was set, otherwise throws exception
        print(rest_of_themes.first().selected)

        for theme in rest_of_themes.values("name"):
            self.assertNotIn(theme["name"], rest_of_themes)

        # Make union of querysets
        all_themes = selected_themes.union(rest_of_themes).order_by("-selected", "relevancy", "id")

        self.assertGreater(all_themes.count(), rest_of_themes.count())

        print(all_themes)

        # First items should be two select and have the same order
        self.assertEqual(
            [theme["name"] for theme in all_themes[:len(selected_themes_list)].values("name")],
            selected_themes_list
        )

        paginator = Paginator(object_list=all_themes,per_page=4)

        page1 = paginator.get_page(1)
        page2 = paginator.get_page(page1.next_page_number())

        breakpoint()
        # Convert querysets to a list, so that they can be compared on equality
        self.assertEqual(list(page1.object_list), list(all_themes[:len(selected_themes_list)]))
        self.assertEqual(list(page2.object_list), list(all_themes[len(selected_themes_list):-1]))

