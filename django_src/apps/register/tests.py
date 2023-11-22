from datetime import date
from typing import cast
from pathlib import Path
from django.http.response import HttpResponse
from django.conf import settings

from django.template.response import TemplateResponse

from django.urls.base import reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile

from django_src.apps.register.models import (
    Student, StudentInterest,
    Mentor, MentorExperience,
    Faculty, Carreer, CarrerSpecialization,
    InterestTheme,
)
from django_src.apps.register.forms import (
    StudentForm,
    UserCreationForm,
)
from .upload_data import create_carreers
from .views import SelectCarreraView, SelectCarrerSpecialization, SelecThemeView, step_urls
import django_src.apps.register.complete_profile_view as profile_view
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from django.http.response import HttpResponseNotAllowed
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect
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

class ViewTests(TestCase):
    """
    Tests for select SelectCarreraView and SelectCarrerSpecialization 
    """

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

class CompleteStudentProfileViewTest(TestCase):
    def setUp(self):
        self.url = reverse("register:complete_profile")

        self.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        self.computacion = self.faculty.carreers.create(name="Computación")
        self.matematicas = self.faculty.carreers.create(name="Matemáticas")

        self.computacion_interests = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Matemáticas"),
                InterestTheme(name="Programación"),
            ]
        )

        self.mates_interest_set = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Cálculo"),
                InterestTheme(name="Límites"),
            ]
        )

        self.ati = self.computacion.carrerspecialization_set.create(
            name="Aplicaciones Tecnología Internet",
        )

        self.elementos = self.matematicas.carrerspecialization_set.create(
            name="Elementos",
        )

        self.computacion.interest_themes.add(*self.computacion_interests)
        self.matematicas.interest_themes.add(*self.mates_interest_set)
        self.base_data = {
            "email": "diego@mail.com",
            "first_name": "Diego",
            "last_name": "Sánchez",
            "profile": "estudiante",
            # https://docs.djangoproject.com/en/stable/ref/forms/api/#binding-uploaded-files-to-a-form
            "voucher": SimpleUploadedFile(name="voucher.pdf", content=b"file_content", content_type="application/pdf"),
            "profile_pic": SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            ),
            "action": "create_student",
        }

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_student_form
    def test_student_form(self):
        """
        Just a quick test to find out if to_field_name works
        """
        form = StudentForm(
            initial={
                "carreer": self.computacion.name,
                "specialization": self.ati.name,
            }
        )
        # values of the fields should be those specified in the initial dict
        self.assertEqual(form["carreer"].value(), self.computacion.name)
        self.assertEqual(form["specialization"].value(), self.ati.name)

        pass
    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_get
    def test_get(self):
        """
        Test the first visit to the page
        """
        request = RequestFactory().get(
            path=self.url,
            data={
                "carreer": self.computacion,
            },
        )

        # Cast is used for type hints
        # https://stackoverflow.com/questions/71845596/python-typing-narrowing-type-from-function-that-returns-a-union
        response  = cast(TemplateResponse,profile_view.complete_profile_view(request))

        # Test that it has the basic urls for the stepper component
        assert response.context_data, "Context data is undefined for the response" # this assert avoids lsp errors

        for key in step_urls.keys():
            self.assertIsNotNone(response.context_data["step_urls"][key])


    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_create_student
    def test_create_student(self):
        """
        Test the creation of a student with valid data and all fields filled
        """

        # Valid case for user and student form
        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                "password1": "dev_123456",
                "password2": "dev_123456",
                "carreer": self.computacion.name,
                "interests": self.computacion.interest_themes.values_list("name",flat=True)
            }
        )

        # mock htmx
        request.htmx = True

        # --- Test the context --- #
        context = profile_view.get_context(request, action=self.base_data["action"])
        assert context, "context is None"

        user_form_valid = cast(UserCreationForm, context["user_form"])
        student_form_valid = cast(StudentForm,context["student_form"])

        self.assertTrue(user_form_valid.is_valid(), msg=dict(user_form_valid.errors))
        self.assertTrue(student_form_valid.is_valid(), msg=dict(student_form_valid.errors))

        response = cast(HttpResponseClientRedirect,profile_view.complete_profile_view(request))

        self.assertEqual(response.status_code, 200)

        # This will probably change to be a redirect request
        self.assertEqual(response.url, "/register/success")

        # Test that the voucher was saved
        student = Student.objects.get(user__email=user_form_valid.cleaned_data['email'])

        self.assertEqual(student.user.username, student.user.email)

        voucher_path = Path(student.voucher.path)
        self.assertTrue(voucher_path.exists())

        # Cleanup action remove the voucher
        student.voucher.delete()

        # Make sure the voucher was delete
        assert voucher_path.exists() == False, "Voucher was not deleted"

        # Test that the profile pic was saved
        profile_pic_path = Path(student.user.profile_pic.path)
        self.assertTrue(profile_pic_path.exists())

        # Cleanup action remove the profile picture file
        student.user.profile_pic.delete()

        # Make sure the profile picture was delete
        assert profile_pic_path.exists() == False, "Voucher was not deleted"


    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_password_do_not_match
    def test_password_do_not_match(self):
        """
        The user form is invalid
        """

        # Passwords do not match
        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                "password1": "@ds*1234567",
                "password2": "@ds*12345678",
                "specialization": self.ati.name,
                "carreer": self.computacion.name,
            }
        )

        # mock htmx
        request.htmx = True

        context = profile_view.get_context(request, action=self.base_data["action"])

        # Make sure that the contex is not null
        assert context, "The context is None"

        # Get forms
        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["student_form"])

        # Check forms validity
        self.assertTrue(student_form.is_valid(), msg=student_form.errors)
        self.assertFalse(user_form.is_valid(), msg=user_form.errors)

        # Check that the password error is in the password2 field
        self.assertIn("password2", user_form.errors)

        response = cast(HttpResponse,profile_view.complete_profile_view(request))

        from html.parser import HTMLParser

        res_html = response.content.decode("utf-8")

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_specialization_is_invalid
    def test_specialization_is_invalid(self):
        """
        Test an invalid case: the specialization is not in the carreer
        """

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                # Passwords do match
                "password1": "dev_123456",
                "password2": "dev_123456",
                # Elementos specialization does not belongs to computer science carreer
                "specialization": self.elementos.name,
                "carreer": self.computacion.name,
            }
        )

        context = profile_view.get_context(request, action=self.base_data["action"])

        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["student_form"])

        # Check forms validity
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertFalse(student_form.is_valid(), msg=student_form.errors)

        self.assertIn("specialization", student_form.errors)

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_specialization_interest_validation
    def test_specialization_interest_validation(self):
        """
        Test that student can't have specialization an interest themes at the same time
        """

        # Valid case for user and student form
        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                "password1": "dev_123456",
                "password2": "dev_123456",
                "specialization": self.ati.name,
                "carreer": self.computacion.name,
                "interests": self.matematicas.interest_themes.values_list("name",flat=True)
            }
        )

        # mock htmx
        request.htmx = True

        # --- Test the context --- #
        context = profile_view.get_context(request, action=self.base_data["action"])
        assert context, "context is None"

        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["student_form"])

        # Check forms validity
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertFalse(student_form.is_valid(), msg=student_form.errors)

        self.assertIn("interests", student_form.errors)

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_no_specialization_and_no_interest
    def test_no_specialization_and_no_interest(self):

        # Valid case for user and student form
        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                "password1": "dev_123456",
                "password2": "dev_123456",
                "carreer": self.computacion.name,
            }
        )

        # mock htmx
        request.htmx = True

        # --- Test the context --- #
        context = profile_view.get_context(request, action=self.base_data["action"])
        assert context, "context is None"

        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["student_form"])

        # Check forms validity
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertFalse(student_form.is_valid(), msg=student_form.errors)

        # Non field errors should appear
        self.assertIn("__all__", student_form.errors)

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_interest_theme_invalid
    def test_interest_theme_invalid(self):
        """
        Test that interest_themes are invalid, because it belongs to another carreer
        """

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.base_data,
                # Passwords do match
                "password1": "dev_123456",
                "password2": "dev_123456",
                "carreer": self.computacion.name,
                "interests": self.matematicas.interest_themes.values_list("name",flat=True)
            }
        )

        context = profile_view.get_context(request, action=self.base_data["action"])

        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["student_form"])


        # Check forms validity
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertFalse(student_form.is_valid(), msg=student_form.errors)

        self.assertIn("interests", student_form.errors)
