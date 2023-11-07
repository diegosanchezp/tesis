from datetime import date

from django_src.apps.register.models import (
    Student, StudentInterest,
    Mentor, MentorExperience,
    Faculty, Carreer, CarrerSpecialization,
    InterestTheme,
)
from .upload_data import create_carreers
from .views import SelectCarreraView, SelectCarrerSpecialization
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.urls import reverse

# ./manage.py test django_src.apps.register.tests.ModelTests.test_student_model
class ModelTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        self.computacion = self.faculty.carreers.create(name="Computación")

        self.student_user = User.objects.create(
            username="diego",
            first_name="Diego",
            last_name="Sánchez",
            email="diego@mail.com",
        )

        self.mentor_user = User.objects.create(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
        )

        self.student = Student.objects.create(
            user=self.student_user,
            carreer=self.computacion,
        )

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

        breakpoint()

    def test_bulk(self):

        interests = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Matemáticas"),
                InterestTheme(name="Programación"),
            ]
        )

        self.computacion.interest_themes.add(*interests)
        self.assertTrue(self.computacion.interest_themes.count(), 2)

        breakpoint()

    def test_upload_datascript(self):
        create_carreers()

class FormTests(TestCase):

    def test_career_form(self):
        pass

class ViewTests(TestCase):

    def setUp(self):

        self.ciencias = Faculty.objects.create(
            name="Ciencias",
        )

        # Create two carreers
        self.computacion = self.ciencias.carreers.create(name="Computación")
        self.quimica = self.ciencias.carreers.create(name="Química")
    # ./manage.py test django_src.apps.register.tests.ViewTests.test_select_search
    def test_select_search(self):


        url = reverse("register:select_carrera")

        # Build the request
        request = RequestFactory().get(
            path=url,
            data={"search": "compu"},
        )

        # Mock htmx attribute
        request.htmx = True

        # Build view
        view = SelectCarreraView()
        view.setup(request)

        # Check that it has facultys
        context = view.get_context_data()
        facultys = context["facultys"]
        self.assertIn("facultys", context, msg="facultys is not in context dict")

        # Check that the search has been correct
        self.assertTrue(facultys.count() == 1)
        self.assertTrue(facultys.first() == self.ciencias)
        self.assertTrue(facultys[0].carreers.count() == 1, msg="Only one carreer should've been shown")
        self.assertTrue(facultys[0].carreers.first() == self.computacion, msg=f"The carrer is not {self.computacion.name}")

        # Process the request, so we can have a response
        response = view.dispatch(request)

        # Check that django-render-block has worked correctly by inspecting 
        # the html on the response body
        self.assertIn("<form", response.content.decode())

    # ./manage.py test django_src.apps.register.tests.ViewTests.test_select_specialization
    def test_select_specialization(self):

        self.ati = self.computacion.carrerspecialization_set.create(
            name="Aplicaciones Tecnología Internet",
        )

        url = reverse("register:select_specialization", kwargs={"name":self.computacion.name})

        # Build the request
        request = RequestFactory().get(
            path=url,
        )

        # Build view
        view = SelectCarrerSpecialization()
        view.setup(request, name=self.computacion.name)
        response = view.dispatch(request)
        context = view.get_context_data()
        self.assertEquals(
            context["specializations_json"],
            [{"name": self.ati.name}]
        )
