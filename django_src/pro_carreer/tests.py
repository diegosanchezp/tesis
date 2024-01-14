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
    RegisterApprovals, RegisterApprovalStates,
    Student,
)

from django_src.pro_carreer import student_pro_carreer_view

from .test_data import (
    create_pro_carreers, create_pro_interes_themes
)

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


        # Wagtail's root page
        cls.root_page = Page.objects.get(slug='root')

        pro_careers = create_pro_carreers()

        cls.pro_careers_index = pro_careers.pro_career_index
        cls.frontend_dev = pro_careers.frontend_dev
        cls.fullstack_dev = pro_careers.fullstack_dev

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
        graph_data = student_pro_carreer_view.get_graph_data()
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
