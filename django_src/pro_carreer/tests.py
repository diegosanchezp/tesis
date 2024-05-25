from os import environ
from django.urls.base import reverse_lazy
from django.db.models.query import QuerySet

from django.contrib.contenttypes.models import ContentType

from wagtail.models import (
    Page,
)

from django_src.pro_carreer.models import (
    ProfessionalCarreer,
    ProCarreerIndex,
)

from django_src.apps.register.models import (
    CarrerSpecialization,
    InterestTheme,
    ThemeSpecProCarreer,
    Student,
)

from django_src.pro_carreer import student_pro_carreer_view

from .test_data import (
    ProCarreerData, create_pro_interes_themes
)
from .forms import ThemeSpecRelateForm, RelateActions, DeleteThemeSpecRelateForm

from django_src.apps.register.test_utils import TestCaseWithData
# Create your tests here.

# ./manage.py test --keepdb django_src.pro_carreer.tests.TestStudentProCarreerView
class TestStudentProCarreerView(TestCaseWithData):
    """
    Test Scenario: Student has specialization, ie doesn't have interests
    Pre conditions he's logged-in and is approved.
    """

    def setUp(self):
        super().setUp()
        self.url = reverse_lazy("pro_carreers:student_carreer_match")

        # Login the student user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.student_user, password="dev123456",
        ))

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.student_type = ContentType.objects.get_for_model(Student)

        cls.interest_theme_type = ContentType.objects.get_for_model(InterestTheme)
        cls.carreer_spec_type = ContentType.objects.get_for_model(CarrerSpecialization)

        # Add self.ati as a specialization of computacion
        cls.computacion.carrerspecialization_set.add(
            cls.ati
        )
        pro_carreers = ProCarreerData()
        pro_carreers.create()

        cls.frontend_dev = pro_carreers.frontend_dev
        cls.fullstack_dev = pro_carreers.fullstack_dev
        cls.pro_career_index = pro_carreers.pro_career_index

        # ---- Scenario: Student has interests, ie doesn't have specialization ----
        interest_themes_match = create_pro_interes_themes()

        cls.html_theme = interest_themes_match.html_theme
        cls.css_theme = interest_themes_match.css_theme
        cls.css_frontend_dev = interest_themes_match.css_frontend_dev
        cls.css_fullstack = interest_themes_match.css_fullstack

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestStudentProCarreerView.test_student_with_interests
    def test_student_with_interests(self):

        self.student.interests.add(self.html_theme, self.css_theme)
        self.assertEqual(self.student.interests.count(), 2)

        response = self.client.get(
            path=self.url,
            # mock htmx
            # headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)

        request = response.wsgi_request

        student_from_view = student_pro_carreer_view.get_student(request)
        self.assertEqual(student_from_view.pk, self.student.pk)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = student_pro_carreer_view.get_queryset(request)

        # Two professional carreers should match, given the student interests
        self.assertEqual(student_match_procarreers.count(), 2, msg=student_match_procarreers)

        # Frontend dev should be the first matched carreer
        self.assertEqual(student_match_procarreers.first().title, self.frontend_dev.title, msg=student_match_procarreers)

        # Fullstack dev should be the second matched carreer
        self.assertEqual(student_match_procarreers[1].title, self.fullstack_dev.title, msg=student_match_procarreers)

        # self.assertEqual(ThemeSpecProCarreer.objects.count(), 2)
        # self.assertEqual(ThemeSpecProCarreer.objects.filter(content_type=interest_theme_type).count(), 1)
        # self.assertEqual(ThemeSpecProCarreer.objects.filter(content_type=carreer_spect_type).count(), 1)
        # How the pro carreer matches can be accessed from an interest theme instance
        # self.assertEqual(self.ati.pro_carreers_match.count(), 1)
        # html_theme.pro_carreer.add(html_rel)
        # html_theme.save()

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestStudentProCarreerView.test_student_with_specialization
    def test_student_with_specialization(self):

        # Nuke the student interests, by removing all objects from the related object set
        # self.student.interests.clear()

        # Set ATI as student specialization
        self.student.specialization = self.ati
        self.student.save()

        self.assertEqual(self.student.specialization.pk, self.ati.pk)

        self.assertEqual(self.student.interests.count(), 0)

        response = self.client.get(
            path=self.url,
        )

        request = response.wsgi_request

        student_from_view = student_pro_carreer_view.get_student(request)

        self.assertEqual(student_from_view.pk, self.student.pk)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = student_pro_carreer_view.get_queryset(request)

        # Two professional carreers should match, given the student interests
        self.assertEqual(student_match_procarreers.count(), 2, msg=student_match_procarreers)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestStudentProCarreerView.test_get_graph_data
    def test_get_graph_data(self):

        response = self.client.get(
            path=self.url,
        )

        request = response.wsgi_request
        graph_data = student_pro_carreer_view.get_graph_data(request)
        self.assertIn("nodes", graph_data)
        self.assertIn("edges", graph_data)
        self.assertGreaterEqual(len(graph_data["nodes"]), 0)
        self.assertGreaterEqual(len(graph_data["edges"]), 0)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestStudentProCarreerView.test_student_is_approved
    def test_student_is_approved(self):

        with self.subTest("Case user is logged in and is a student"):
            response = self.client.get(
                path=self.url,
            )

            self.assertEqual(response.status_code, 200)

        with self.subTest("Case user is logged out"):

            self.client.logout()

            response = self.client.get(
                path=self.url,
            )

            # Should be redirected to login page
            self.assertEqual(response.status_code, 302)

# ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView
class TestSpecThemeMatchView(TestCaseWithData):
    """
    Test the Wagtail view that creates the matches between the professional carreers
    and the specialization themes
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        pro_carreers = ProCarreerData()
        pro_carreers.create()

        cls.frontend_dev = pro_carreers.frontend_dev
        cls.fullstack_dev = pro_carreers.fullstack_dev
        cls.pro_career_index = pro_carreers.pro_career_index


        cls.html_theme, created = InterestTheme.objects.get_or_create(
            name="HTML",
        )

    def setUp(self):

        super().setUp()

        self.url = reverse_lazy("relate_theme_spec", kwargs={"pk_pro_career":self.fullstack_dev.pk})

        # Login the admin user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.admin_user, password=environ["ADMIN_PASSWORD"],
        ))

        self.theme_type = ContentType.objects.get_for_model(InterestTheme)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView.test_create_spec_match
    def test_create_spec_match(self):

        # Check that ati doesnt have any weighted matches with the fullstack dev
        spec_type = ContentType.objects.get_for_model(CarrerSpecialization)

        self.assertEqual(self.ati.pro_carreers_match.filter(content_type=spec_type).count(), 0)

        response = self.client.post(
            path=self.url,
            headers={"HX-Request": "true"},
            data={
                # Action forms
                "action": RelateActions.RELATE_THEME_SPEC,
                "model_type": CarrerSpecialization.__name__,
                # Theme spec form fields
                "weight": 10,
                "theme_spec": self.ati.pk,
            }
        )

        self.assertEqual(response.status_code, 200)

        try:
            spec_match = self.ati.pro_carreers_match.get(pro_career=self.fullstack_dev)
        except:
            self.fail("The professional career match was not created")

        response_html = response.content.decode()
        self.assertIn("<tr", response_html)
        self.assertIn(spec_match.content_object.name, response_html)


    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView.test_create_theme_match
    def test_create_theme_match(self):

        self.assertEqual(self.html_theme.pro_carreers_match.filter(content_type=self.theme_type).count(), 0)

        response = self.client.post(
            path=self.url,
            headers={"HX-Request": "true"},
            data={
                # Action forms
                "action": RelateActions.RELATE_THEME_SPEC,
                "model_type": InterestTheme.__name__,
                # Theme spec form fields
                "weight": 10,
                "theme_spec": self.html_theme.pk,
            }
        )

        self.assertEqual(response.status_code, 200)

        try:
            theme_match = self.html_theme.pro_carreers_match.get(pro_career=self.fullstack_dev)
        except ThemeSpecProCarreer.DoesNotExist:
            self.fail("The theme relation with professional careermatch was not created")

        response_html = response.content.decode()

        self.assertIn(theme_match.content_object.name, response_html)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView.test_forms
    def test_forms(self):

        form = ThemeSpecRelateForm(
            model=CarrerSpecialization,
            data={
                "weight": 10,
                "theme_spec": self.ati.pk,
            }
        )

        self.assertTrue(form.is_valid(), msg=form.errors)
        self.assertEqual(form.model_type, CarrerSpecialization.__name__)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView.test_delete_weighted_spec
    def test_delete_weighted_spec(self):

        # Create a weighted match
        weighted_spec = self.ati.pro_carreers_match.create(
            pro_career=self.fullstack_dev,
            weight=10,
        )

        response = self.client.post(
            path=self.url,
            headers={"HX-Request": "true"},
            data={
                "action": RelateActions.DELETE_THEME_SPEC.value,
                "model_type": CarrerSpecialization.__name__,
                "theme_spec": self.ati.pk,
                "weighted_spec": weighted_spec.pk,
            }
        )

        response_html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_html, "ok")

        # Create again, because is delete by the call to the view
        weighted_spec, created = self.ati.pro_carreers_match.get_or_create(
            pro_career=self.fullstack_dev,
            weight=10,
        )
        self.assertTrue(created)

        valid_form = DeleteThemeSpecRelateForm(
            model = CarrerSpecialization,
            data={
                "theme_spec": self.ati.pk,
                "weighted_spec": weighted_spec.pk,
            }
        )

        self.assertTrue(valid_form.is_valid(), msg=valid_form.errors)

        # Invalid case: when the weighted spec doesnt belong to the specialization

        html_theme, created = InterestTheme.objects.get_or_create(
            name="HTML",
        )

        html_fullstack_dev = html_theme.pro_carreers_match.create(
            weight="10", pro_career=self.fullstack_dev,
        )

        # Check Invalid case: when the weighted spec doesnt belong to the 
        # theme or spec
        invalid_form = DeleteThemeSpecRelateForm(
            model = CarrerSpecialization,
            data={
                "theme_spec": self.ati.pk,
                "weighted_spec": html_fullstack_dev.pk,
            }
        )

        self.assertFalse(invalid_form.is_valid())
        # Should render error
        self.assertIn("__all__", invalid_form.errors)

    # ./manage.py test --keepdb django_src.pro_carreer.tests.TestSpecThemeMatchView.test_delete_weighted_theme
    def test_delete_weighted_theme(self):

        # Create a weighted match
        weighted_spec = self.html_theme.pro_carreers_match.create(
            pro_career=self.fullstack_dev,
            weight=10,
        )

        response = self.client.post(
            path=self.url,
            headers={"HX-Request": "true"},
            data={
                "action": RelateActions.DELETE_THEME_SPEC.value,
                "model_type": InterestTheme.__name__,
                "theme_spec": self.html_theme.pk,
                "weighted_spec": weighted_spec.pk,
            }
        )

        response_html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertFalse(ThemeSpecProCarreer.objects.filter(pk=weighted_spec.pk, content_type=self.theme_type).exists())

