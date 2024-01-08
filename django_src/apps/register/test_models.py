from datetime import date

import django.db
from django.db.models.query import QuerySet
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponse
from django.urls.base import reverse_lazy

from wagtail.models import (
    Page,
)

from django_src.pro_carreer.models import (
    ProfessionalCarreer,
    ProCarreerIndex,
)
from django_src.apps.register.models import (
    CarrerSpecialization,
    Student,
    Mentor, MentorExperience,
    Faculty,
    InterestTheme,
    ThemeSpecProCarreer,
)

from django_src.pro_carreer import student_pro_carreer_view
# ./manage.py test --keepdb django_src.apps.register.test_models.ModelTests
class ModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()

        cls.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        cls.computacion = cls.faculty.carreers.create(name="Computación")

        cls.student_user = User.objects.create(
            username="diego",
            first_name="Diego",
            last_name="Sánchez",
            email="diego@mail.com",
        )

        cls.student_user.set_password("dev123456")
        cls.student_user.save()
        cls.student = Student.objects.create(
            user=cls.student_user,
            carreer=cls.computacion,
        )

        cls.mentor_user = User.objects.create(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
        )
        cls.mentor_user.set_password("dev123456")
        cls.mentor_user.save()


    def setUp(self):
        super().setUp()


    # ./manage.py  test --keepdb django_src.apps.register.test_models.ModelTests.test_student_model
    def test_student_model(self):

        ati = self.computacion.carrerspecialization_set.create(
            name="Aplicaciones Tecnología Internet",
        )

        ati.students.add(self.student)

        self.assertEqual(ati.students.count(), 1)
        self.assertEqual(ati.students.first().user.first_name, self.student.user.first_name)

        mates = self.student.interests.create(
            name="Matemáticas",
        )

        programacion = self.student.interests.create(
            name="Programación",
        )

        self.computacion.interest_themes.add(mates)
        self.computacion.interest_themes.add(programacion)
        self.assertEqual(self.computacion.interest_themes.count(),2)

        self.assertEqual(self.student.interests.count(),2)


    def test_mentor_model(self):
        mentor = Mentor.objects.create(
            user=self.mentor_user,
            carreer=self.computacion,
        )

        # the students to whom the mentor has mentored
        mentor.students.add(self.student)

        self.assertEqual(self.student.mentor_set.count(), 1)
        # These will be used when registering the mentor
        mentor.experiences.create(
            name="Front end developer",
            company="Meta",
            current=False,
            init_year=date(year=2010,month=12,day=1),
            end_year=date(year=2012,month=6,day=12),
            description="Doing frontend things @Meta formerly Facebook",
        )

        mentor.experiences.create(
            name="Front end developer",
            company="Google",
            init_year=date(year=2012,month=6,day=19),
            current=True,
            description="Doing frontend things",
        )
        self.assertEqual(mentor.experiences.count(), 2)


    # ./manage.py test --keepdb django_src.apps.register.test_models.ModelTests.test_exp_uniqueness
    def test_exp_uniqueness(self):

        mentor = Mentor.objects.create(
            user=self.mentor_user,
            carreer=self.computacion,
        )

        exp1 = MentorExperience(
            mentor=mentor,
            name="Full stack developer",
            company="Google",
            init_year=date(2010,1,1),
            end_year=date(2011,1,1),
            current=False,
            description="Full Stack Dev @ Google",
        )

        exp1.save()

        exp2 = MentorExperience(
            mentor=mentor,
            name="Full stack developer",
            company="Google",
            init_year=date(2010,1,1),
            end_year=date(2011,1,1),
            current=False,
            description="Full Stack Dev @ Google",
        )

        with self.assertRaises(django.db.IntegrityError):
            exp2.save()

    def test_bulk(self):

        interests = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Matemáticas"),
                InterestTheme(name="Programación"),
            ]
        )

        self.computacion.interest_themes.add(*interests)
        self.assertTrue(self.computacion.interest_themes.count(), 2)


    # def test_upload_datascript(self):
    #     create_carreers()

    # ./manage.py test --keepdb django_src.apps.register.test_models.ModelTests.test_query_pro_carreer_matches
    def test_query_pro_carreer_matches(self):


        interest_theme_type = ContentType.objects.get_for_model(InterestTheme)
        carreer_spec_type = ContentType.objects.get_for_model(CarrerSpecialization)

        # Add ati as a specialization of computacion
        ati: CarrerSpecialization = self.computacion.carrerspecialization_set.create(
            name="Aplicaciones Tecnología Internet",
        )

        # Wagtail's root page
        root_page = Page.objects.get(slug='root')

        # Create some professional carreers
        pro_career_index: ProCarreerIndex = root_page.add_child(
            instance=ProCarreerIndex(
                title="Professional Carreers",
            ),
        )

        frontend_dev: ProfessionalCarreer = pro_career_index.add_child(
            instance=ProfessionalCarreer(
                title="Frontend Developer",
                short_description="Makes WEB GUI stuff",
            )
        )

        fullstack_dev: ProfessionalCarreer = pro_career_index.add_child(
            instance=ProfessionalCarreer(
                title="Full stack Developer",
                short_description="Makes WEB GUIs & codes backend services",
            )
        )

        # ---- Scenario: Student has interests, ie doesn't have specialization ----

        # Themes
        html_theme = InterestTheme.objects.create(
            name="HTML",
        )

        css_theme = InterestTheme.objects.create(
            name="CSS",
        )

        # Relate html to frontend development
        html_theme.pro_carreers_match.create(
            weight="10", pro_career=frontend_dev,
        )

        # Relate css to frontend development
        css_theme.pro_carreers_match.create(
            weight="10", pro_career=frontend_dev,
        )

        # Relate css to full development
        css_theme.pro_carreers_match.create(
            weight="8", pro_career=fullstack_dev,
        )

        self.student.interests.add(html_theme, css_theme)
        self.assertEqual(self.student.interests.count(), 2)

        url = reverse_lazy("pro_carreers:student_carreer_match")

        # Begin testing the view
        with self.subTest("Test Scenario: Student has interests, ie doesn't have specialization"):

            # Login the student user, need it to populate request.user
            self.assertTrue(self.client.login(
                username=self.student_user, password="dev123456",
            ))

            response = self.client.get(
                path=url,
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
            self.assertEqual(student_match_procarreers.first().title, frontend_dev.title, msg=student_match_procarreers)

            # Fullstack dev should be the second matched carreer
            self.assertEqual(student_match_procarreers[1].title, fullstack_dev.title, msg=student_match_procarreers)

        # ---- Scenario: Student has specialization (ie, no interests themes) ----

        # Nuke the student interests, by removing all objects from the related object set
        self.student.interests.clear()

        self.assertEqual(self.student.interests.count(), 0)

        # Set ATI as student specialization
        self.student.specialization = ati
        self.student.save()

        self.assertEqual(self.student.specialization.pk, ati.pk)

        # Put weight 10 (high correlation) to frontend_dev and fullstack_dev
        ati.pro_carreers_match.create(
            weight="10", pro_career=frontend_dev,
            content_object=ati,
        )

        ati.pro_carreers_match.create(
            weight="10", pro_career=fullstack_dev,
            content_object=ati,
        )

        with self.subTest("Test Scenario: Student has specialization, ie doesn't have interests"):

            self.assertTrue(self.client.login(
                username=self.student_user, password="dev123456",
            ))

            student_from_view = student_pro_carreer_view.get_student(request)
            self.assertEqual(student_from_view.pk, self.student.pk)

            response = self.client.get(
                path=url,
                # mock htmx
                # headers={"HX-Request": "true"},
            )

            request = response.wsgi_request

            student_match_procarreers: QuerySet[ProfessionalCarreer] = student_pro_carreer_view.get_queryset(request)
            # Two professional carreers should match, given the student interests
            self.assertEqual(student_match_procarreers.count(), 2, msg=student_match_procarreers)

        # self.assertEqual(ThemeSpecProCarreer.objects.count(), 2)
        # self.assertEqual(ThemeSpecProCarreer.objects.filter(content_type=interest_theme_type).count(), 1)
        # self.assertEqual(ThemeSpecProCarreer.objects.filter(content_type=carreer_spect_type).count(), 1)
        # How the pro carreer matches can be accessed from an interest theme instance
        # self.assertEqual(ati.pro_carreers_match.count(), 1)
        # html_theme.pro_carreer.add(html_rel)
        # html_theme.save()
