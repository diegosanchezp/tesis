from datetime import date

from django.urls.base import reverse_lazy

from django_src.apps.register.models import (
    Student, StudentInterest,
    Mentor, MentorExperience,
    Faculty, Carreer, CarrerSpecialization,
    InterestTheme,
)
from .upload_data import create_carreers
from .views import SelectCarreraView, SelectCarrerSpecialization, SelecThemeView
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
class InterestThemeViewTest(TestCase):
    def setUp(self):

        self.ciencias = Faculty.objects.create(
            name="Ciencias",
        )

        # Create two carreers
        self.computacion = self.ciencias.carreers.create(name="Computación")

        self.computacion.interest_themes.create(name="Matemáticas",)
        self.computacion.interest_themes.create(name="Programación",)

        self.computacion.interest_themes.create(name="HTML"),
        self.computacion.interest_themes.create(name="Javascript"),
        self.computacion.interest_themes.create(name="CSS"),
        self.computacion.interest_themes.create(name="C++"),
        self.computacion.interest_themes.create(name="UI/UX"),
        self.computacion.interest_themes.create(name="Trabajo en equipo"),
        self.computacion.interest_themes.create(name="Gestion de Recursos"),
        self.computacion.interest_themes.create(name="BPM"),
        # Build view
        self.view = SelecThemeView()

        self.url = reverse("register:select_themes", kwargs={"name":self.computacion.name})

    # ./manage.py test django_src.apps.register.tests.InterestThemeViewTest.test_normal_get
    def test_normal_get(self):
        """
        A normal get request

        When an user had just completed the previous step and hasn't choosen any themes

        AKA the default state of the select themes page
        """

        # Build the request
        request = RequestFactory().get(
            path=self.url,
        )

        request.htmx = False

        self.view.setup(request, name=self.computacion.name)

        response = self.view.dispatch(request)
        context = self.view.get_context_data()

        url_spec = reverse_lazy("register:select_specialization", kwargs={"name":self.computacion.name})

        self.assertEquals(
            context["step_urls"]["specialization"],
            url_spec,
        )

        self.assertEquals(
            context["carreer"],
            self.computacion,
        )

        self.assertEquals(
            context["object_list"].count(),
            self.view.paginate_by,
        )

    # ./manage.py test django_src.apps.register.tests.InterestThemeViewTest.get_page_with_htmx
    def get_page_with_htmx(self):
        """
        HTMX calls the view with query parameter "page"
        To get a new set of themes.

        No themes had been previously selected
        """

        # Build the request
        request = RequestFactory().get(
            path=self.url,
            # Set page to two because the alredy returns the first page
            data={"page": 2}
        )

        # Mock htmx middleware
        request.htmx = True

        # Set number of items in a page
        self.view.paginate_by = 4
        self.view.setup(request, name=self.computacion.name)

        response = self.view.dispatch(request)
        context = self.view.get_context_data()
        object_list = context["object_list"]

        # Check that it has returned the right ammount of themes
        self.assertEqual(len(object_list), self.view.paginate_by)

        # Check that second page has the correct items
        for theme in self.computacion.interest_themes.order_by("name")[4:8].values("name"):
            self.assertIn(
                theme["name"],
                [object_themes["name"] for object_themes in object_list.values("name")],
            )

        # Print the rendered content don't know how to test it
        print(response.content.decode())

    # ./manage.py test django_src.apps.register.tests.InterestThemeViewTest.get_with_themes
    def get_with_themes(self):
        """
        The previous steps makes a request and themes have been previously selected

        Please see the headless tests.model_query.TestQuerys.test_themes_pagination
        """
        selected_themes_list = ["Trabajo en equipo", "Matemáticas"]

        #----------------
        # Themes had been previously selected and whe
        # are visiting the page again
        #----------------

        # Build the request
        request = RequestFactory().get(
            path=self.url,
            data={
                "theme": selected_themes_list,
                # not having the page param is the same as
                # "page": 1,
            }
        )

        request.htmx = False

        # Set number of items in a page
        self.view.paginate_by = 4
        self.view.setup(request, name=self.computacion.name)

        response = self.view.dispatch(request)

        # Selected themes are set in the view
        self.assertEqual(
            self.view.selected_themes_list,
            selected_themes_list
        )

        context = self.view.get_context_data()

        # Object list is the queryset that a page returns
        first_page_object_list = context["object_list"]

        # First items should be two select and have the same order
        self.assertEqual(
            [theme["name"] for theme in first_page_object_list[:2].values("name")],
            selected_themes_list
        )

        # Page should have 4 items
        self.assertEqual(
            # .count() doesn't works, gives 1 less, use len() instead
            len(first_page_object_list),
            self.view.paginate_by
        )

        #----------------
        # Get a page with htmx
        #----------------

        # Request a second page with selected themes
        page = 2
        request = RequestFactory().get(
            path=self.url,
            data={
                "theme": selected_themes_list,
                "page": page,
            }
        )
        # Mock htmx
        request.htmx = True

        self.view.setup(request, name=self.computacion.name)
        response = self.view.dispatch(request)
        context = self.view.get_context_data()

        self.assertEqual(context["page_obj"].number, page)

        second_page_object_list = context["object_list"]

        # If we request a second page, then the items of the second page shouldn't be in the first one
        for theme in second_page_object_list.values("name"):
            self.assertNotIn(
                theme["name"],
                [theme["name"] for theme in first_page_object_list.values("name")],
            )
