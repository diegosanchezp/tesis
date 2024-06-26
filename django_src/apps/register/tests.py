from datetime import date, timedelta
import json
from typing import cast
from pathlib import Path

from django.http.response import HttpResponse
from django.http.request import QueryDict
from django.conf import settings

from django.template.response import TemplateResponse
from django import forms

from django.urls.base import reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile


from django_src.apps.register.models import (
    Student,
    Mentor, MentorExperience,
    Faculty, Carreer,
    InterestTheme,
    RegisterApprovals, RegisterApprovalStates,
)
from django_src.apps.register.forms import (
    StudentForm,
    UserCreationForm,
    get_MentorExperienceFormSet,
)
from .views import SelectCarreraView, SelectCarrerSpecialization, SelecThemeView, step_urls
from .add_mentor_exp_view import add_mentor_exp_view, get_POST_context_data, get_GET_context_data, actions as exp_actions
from .forms import MentorExperienceForm, QueryForm, MentorForm
import django_src.apps.register.complete_profile_view as profile_view
from django.test import TestCase, RequestFactory

from django.http.response import HttpResponseNotAllowed
from django.urls import reverse
from django_htmx.http import HttpResponseClientRedirect


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
    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_valid_get
    def test_valid_get(self):
        """
        Test the first visit to the page
        """
        request = RequestFactory().get(
            path=self.url,
            data={
                "carreer": self.computacion,
                "profile": "estudiante",
            },
        )

        # Cast is used for type hints
        # https://stackoverflow.com/questions/71845596/python-typing-narrowing-type-from-function-that-returns-a-union
        response  = cast(TemplateResponse,profile_view.complete_profile_view(request))

        # Test that it has the basic urls for the stepper component
        assert response.context_data, "Context data is undefined for the response" # this assert avoids lsp errors

        for key in step_urls.keys():
            self.assertIsNotNone(response.context_data["step_urls"][key])

    # ./manage.py test --keepdb django_src.apps.register.tests.CompleteStudentProfileViewTest.test_invalid_get
    def test_invalid_get(self):
        """
        """

        request = RequestFactory().get(
            path=self.url,
            data={
                # Set an invalid carreer
                "carreer": "WADSADSa",
                "profile": "",
            },
        )

        response = cast(TemplateResponse,profile_view.complete_profile_view(request))

        ctx = profile_view.get_context(request, action=self.base_data["action"])

        self.assertIn("query_form", ctx)

        query_form = cast(QueryForm, ctx["query_form"])

        self.assertFalse(query_form.is_valid())
        print(query_form.errors.as_data())
        print(query_form.errors)
        self.assertIn("carreer", query_form.errors)
        # self.assertIn("<form", response.content.decode("utf-8"))

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
        student_form_valid = cast(StudentForm,context["entity_form"])

        self.assertTrue(user_form_valid.is_valid(), msg=dict(user_form_valid.errors))
        self.assertTrue(student_form_valid.is_valid(), msg=dict(student_form_valid.errors))

        response = cast(HttpResponseClientRedirect,profile_view.complete_profile_view(request))

        self.assertEqual(response.status_code, 200)

        # This will probably change to be a redirect request
        self.assertEqual(response.url, "/register/success/")

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
        student_form = cast(StudentForm,context["entity_form"])

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
        student_form = cast(StudentForm,context["entity_form"])

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
        student_form = cast(StudentForm,context["entity_form"])

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
        student_form = cast(StudentForm,context["entity_form"])

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
                # passwords do match
                "password1": "dev_123456",
                "password2": "dev_123456",
                "carreer": self.computacion.name,
                "interests": self.matematicas.interest_themes.values_list("name",flat=True)
            }
        )

        context = profile_view.get_context(request, action=self.base_data["action"])

        user_form = cast(UserCreationForm, context["user_form"])
        student_form = cast(StudentForm,context["entity_form"])


        # Check forms validity
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertFalse(student_form.is_valid(), msg=student_form.errors)

        self.assertIn("interests", student_form.errors)

class TestCaseWithData(TestCase):
    """
    Injects models to the test case
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        cls.computacion: Carreer = cls.faculty.carreers.create(name="Computación")
        cls.matematicas = cls.faculty.carreers.create(name="Matemáticas")

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

        cls.ati = cls.computacion.carrerspecialization_set.create(
            name="Aplicaciones Tecnología Internet",
        )

        cls.elementos = cls.matematicas.carrerspecialization_set.create(
            name="Elementos",
        )

        cls.computacion.interest_themes.add(*cls.computacion_interests)
        cls.matematicas.interest_themes.add(*cls.mates_interest_set)

# ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView
class TestCreateMentorExpView(TestCaseWithData):

    def setUp(self):
        super().setUp()
        self.today = date.today()
        self.management_form_data = {
            # Incrementing the TOTAL_FORMS adds a new empty form to the formset
            "form-TOTAL_FORMS": 1,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
        }
        self.form_data={
            "profile": "mentor",
            "carreer": self.computacion.name,
            "form-0-name": "Full stack developer",
            "form-0-company": "Google",
            "form-0-init_year": date(2010,1,1),
            "form-0-end_year": date(2011,1,1),
            "form-0-description": "Full Stack Dev @ Google",
        }

        self.url = reverse("register:add_exp")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_fields
    def test_fields(self):
        field = forms.ModelChoiceField(queryset=Carreer.objects.all(), to_field_name="name")

        # This career do exits
        try:
            field.clean(self.computacion.name)
        except:
            self.fail("Raised exception for an existent carreer")

        with self.assertRaises(forms.ValidationError):
            field.clean("djwakdw")

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_formset
    def test_formset(self):
        MentorExperienceFormSet = get_MentorExperienceFormSet(extra=2, max_num=2)

        form_prefix = MentorExperienceFormSet().prefix
        assert form_prefix, "form prefix is none"

        initial = [
            {
                "name": "Full stack developer",
                "company": "Google",
                "init_year": date(2010,1,1),
                "end_year": date(2015,1,1),
                "id_current": False,
                "description": "Full Stack Dev @ Google",
            },
            {
                "name": "Javascript Soy Dev",
                "company": "Apple",
                "init_year": date(2010,1,1),
                "end_year": date(2015,1,1),
                "id_current": False,
                "description": "Drinking soy lattes @ starbucks and coding my Nodejs app",
            },
        ]
        initial2 = [{'company': 'Google',
                     'current': True,
                     'description': 'jkjljljlk',
                     'end_year': None,
                     'init_year': '2023-10-30',
                     'name': 'Full stack dev'},
                    {'company': 'Apple',
                     'current': True,
                     'description': 'jkjllkjl',
                     'end_year': None,
                     'init_year': '2023-10-29',
                     'name': 'Javascript soy dev'}]


        empty_formset = MentorExperienceFormSet()

        formset = MentorExperienceFormSet(
            data={
                "form-TOTAL_FORMS": 2,
                "form-INITIAL_FORMS": 0,
                "form-MIN_NUM_FORMS": 0,
                "form-MAX_NUM_FORMS": 1000,
                "form-0-name": "Full stack developer",
                "form-0-company": "Google",
                "form-0-init_year": date(2010,1,1),
                "form-0-end_year": date(2011,1,1),
                "form-0-description": "Full Stack Dev @ Google",
                "form-1-name": "Javascript Soy Dev",
                "form-1-company": "",
                "form-1-init_year": date(2015,4,1),
                "form-1-current": True,
                "form-1-description": "Full Stack Dev @ Google",
            }
        )

        # Formset two works for adding an extra form, but validates to invalid
        formset2 = MentorExperienceFormSet(initial=initial2)
        # breakpoint()
        self.assertEqual(formset.total_form_count(), len(initial2))

        # print(formset2)

        invalid_init_year = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
            **self.form_data,
        }
        invalid_init_year["form-0-init_year"] = self.today + timedelta(days=2)

        invalid_init_year_formset = MentorExperienceFormSet(data=invalid_init_year)
        self.assertFalse(invalid_init_year_formset.is_valid())
        self.assertIn("init_year", invalid_init_year_formset.errors[0])

        # Test duplicated experiences names
        # This is how the timline in short form looks like

        # 2015-2016: Full Stack Dev @ Google
        # 2016-2017: Frontend Stack Dev @ Google
        # 2017-*: Full Stack @ Google, current

        one_year_delta = timedelta(days=365)

        timeline_data = {
            f"{form_prefix}-TOTAL_FORMS": 3,
            f"{form_prefix}-INITIAL_FORMS": 0,
            f"{form_prefix}-MIN_NUM_FORMS": 0,
            f"{form_prefix}-MAX_NUM_FORMS": 1000,

            f"{form_prefix}-0-name": "Full stack developer",
            f"{form_prefix}-0-company": "Google",
            f"{form_prefix}-0-init_year": date(2010,1,1),
            f"{form_prefix}-0-end_year": date(2011,1,1),
            f"{form_prefix}-0-description": "Full Stack Dev @ Google",

        }

        timeline_data["form-1-name"] = "Frontend"
        timeline_data["form-1-company"] = self.form_data["form-0-company"]
        timeline_data["form-1-init_year"] = self.form_data["form-0-init_year"] + one_year_delta
        timeline_data["form-1-end_year"] = self.form_data["form-0-end_year"] + one_year_delta
        timeline_data["form-1-current"] = False
        timeline_data["form-1-description"] = "Frontend Dev @ Google"

        timeline_data["form-2-name"] = "Full stack developer"
        timeline_data["form-2-company"] = self.form_data["form-0-company"]
        timeline_data["form-2-init_year"] = timeline_data["form-1-end_year"]
        timeline_data["form-2-current"] = True
        timeline_data["form-2-description"] = "Full Stack Dev @ Google"

        timeline_form = MentorExperienceFormSet(
            data=timeline_data,
        )

        self.assertTrue(timeline_form.is_valid(), msg=timeline_form.errors)


        # Test more than three current experiences

        invalid_timeline = timeline_data.copy()
        invalid_timeline["form-TOTAL_FORMS"] = 4

        # Make sure I have 4 current experiences
        invalid_timeline["form-0-current"] = True
        invalid_timeline["form-1-current"] = True
        invalid_timeline["form-2-current"] = True

        invalid_timeline["form-3-name"] = "Designer"
        invalid_timeline["form-3-company"] = self.form_data["form-0-company"]
        invalid_timeline["form-3-init_year"] = timeline_data["form-1-end_year"]
        invalid_timeline["form-3-current"] = True
        invalid_timeline["form-3-description"] = "Designer @ Google"

        invalid_timeline_form = MentorExperienceFormSet(data=invalid_timeline)
        self.assertTrue(invalid_timeline_form.total_form_count(), invalid_timeline["form-TOTAL_FORMS"])
        self.assertFalse(invalid_timeline_form.is_valid())
        self.assertEqual(len(invalid_timeline_form.non_form_errors()), 1)

        with self.subTest(msg="Invalidates empty fields"):


            data = {
                f"{form_prefix}-TOTAL_FORMS": 1,
                f"{form_prefix}-INITIAL_FORMS": 0,
                f"{form_prefix}-MIN_NUM_FORMS": 0,
                f"{form_prefix}-MAX_NUM_FORMS": 1000,

                f"{form_prefix}-0-name": "a",
                f"{form_prefix}-0-company": "",
                f"{form_prefix}-0-init_year": "",
                f"{form_prefix}-0-end_year": "",
                f"{form_prefix}-0-description": "",
            }

            mentor_form = MentorExperienceForm(data=data, prefix=f"{form_prefix}-0")
            fields = ["name", "company", "description"]
            for field_name in fields:
                # Check min_length
                self.assertIsNotNone(mentor_form.fields[field_name].min_length, msg=f"Field {field_name} has no min_length")
                # Check required
                self.assertTrue(mentor_form.fields[field_name].required)

            print(mentor_form.errors)

            self.assertFalse(mentor_form.is_valid(), msg="")

            # Now do the same tests but with a formset
            mentor_formset = MentorExperienceFormSet(data=data)
            for field_name in fields:
                # Check min_length
                self.assertIsNotNone(mentor_formset.forms[0].fields[field_name].min_length, msg=f"Field {field_name} has no min_length")
                # Check required
                self.assertTrue(mentor_formset.forms[0].fields[field_name].required)

            self.assertFalse(mentor_formset.is_valid(), msg="formset is valid, should be invalid")

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_view_valid
    def test_view_valid(self):
        """
        User is ready to advance to the next view of the multi step form
        """

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.management_form_data,
                **self.form_data,
                "action": exp_actions["validate"],
            }
        )

        # mock htmx
        request.htmx = True

        context = get_POST_context_data(request)
        response = cast(HttpResponse, add_mentor_exp_view(request))

        self.assertEqual(context["action"],exp_actions["validate"])

        formset = context["formset"]

        # formset should be valid
        self.assertTrue(formset.is_valid(), msg=formset.errors)

        htmx_evt_data =  json.loads(response.headers["HX-Trigger"])
        # Initial data should of have been sent to the frontend via an event
        self.assertEqual(htmx_evt_data["formset_validated"]["action"], context["action"], msg=htmx_evt_data.keys())
        query_next_url = QueryDict(mutable=True)
        query_next_url["profile"] = self.form_data["profile"]
        query_next_url["carreer"] = self.form_data["carreer"]

        next_url = f"{reverse_lazy('register:complete_profile')}?{query_next_url.urlencode()}"
        self.assertEqual(
            htmx_evt_data["formset_validated"]["next_url"],
            next_url,
            msg=htmx_evt_data.keys()
        )
        self.assertEqual(htmx_evt_data["formset_validated"]["form_valid"], formset.is_valid(), msg=htmx_evt_data.keys())


    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_add_form
    def test_add_form(self):
        """
        Everything in the formset is valid
        """

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.management_form_data,
                **self.form_data,
                "action": exp_actions["validate_add_form"],
            }
        )
        # mock htmx
        request.htmx = True

        post_context = get_POST_context_data(request)
        post_formset = post_context["formset"]

        # formset should be valid
        self.assertTrue(post_formset.is_valid(), msg=post_formset.errors)

        # TOTAL_FORMS count should have been incremented by one
        self.assertEqual(post_formset.total_form_count(), self.management_form_data["form-TOTAL_FORMS"] + 1)

        response = cast(HttpResponse, add_mentor_exp_view(request))

        htmx_evt_data =  json.loads(response.headers["HX-Trigger"])

        # Initial data should of have been sent to the frontend via an event
        self.assertIn("cleaned_data", htmx_evt_data["formset_validated"], msg=htmx_evt_data.keys())

        # cleaned data has the same number of forms of the formset
        self.assertEqual(len(htmx_evt_data["formset_validated"]["cleaned_data"]), self.management_form_data["form-TOTAL_FORMS"])

        # An item of cleaned_data should not have an id field
        self.assertNotIn("id", htmx_evt_data["formset_validated"]["cleaned_data"][0], msg=htmx_evt_data["formset_validated"]["cleaned_data"])

        # django-render-block should have rendered the new formset
        self.assertIn("<form", response.content.decode("utf-8"))

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_get_localstorage
    def test_get_localstorage(self):
        """
        Set initial formset data with localstorage data
        """

        initial = [
            {
                'company': 'Google',
                'current': True,
                'description': 'jkjljljlk',
                'end_year': None,
                'init_year': '2023-10-30',
                'name': 'Full stack dev'
            },
            {
                'company': 'Apple',
                'current': True,
                'description': 'jkjllkjl',
                'end_year': None,
                'init_year': '2023-10-29',
                'name': 'Javascript soy dev'
            },
            {
                'company': 'STFU',
                'current': True,
                'description': 'aaaaaa',
                'end_year': None,
                'init_year': '2023-10-29',
                'name': 'Javascript soy boy'
            }
        ]



        request = RequestFactory().get(
            path=self.url,
            data={
                "action": "get_form_localstorage",
                "mentor_exp": json.dumps(initial),
            }
        )
        raw_exp = request.GET.get("mentor_exp")

        parsed_initial = json.loads(raw_exp)

        # Parsed has the same
        self.assertEqual(len(parsed_initial), len(initial))

        # Parsed items are equal to the originals
        for idx, exp in enumerate(parsed_initial):
            self.assertEqual(exp, initial[idx])

        request.htmx = True

        context = get_GET_context_data(request)
        formset = context["formset"]
        # The numbers of forms in the formset be the same as the initial
        self.assertEqual(len(formset.forms), len(initial))

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_can_delete
    def test_can_delete(self):

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.management_form_data,
                **self.form_data,
                "action": "add_form",
                "form-0-DELETE": True,
            }
        )

        # mock htmx
        request.htmx = True

        post_context = get_POST_context_data(request)
        post_formset = post_context["formset"]

        # formset should be valid
        self.assertTrue(post_formset.is_valid(), msg=post_formset.errors)
        print(post_formset.as_div())

    # ./manage.py test --keepdb django_src.apps.register.tests.TestCreateMentorExpView.test_view_invalid
    def test_view_invalid(self):
        """
        Invalid formset case:
        fields are missing
        """

        request = RequestFactory().post(
            path=self.url,
            data={
                **self.management_form_data,
                "form-0-name": "",
                "form-0-company": "Google",
                "form-0-init_year": "",
                "form-0-end_year": "",
                "id_form-0-current": False,
                "form-0-description": "",
            }
        )

        # mock htmx
        request.htmx = True

        post_context = get_POST_context_data(request)
        post_formset = post_context["formset"]

        # formset should be invalid
        self.assertFalse(post_formset.is_valid())
        print(post_formset.errors)

        response = cast(HttpResponse, add_mentor_exp_view(request))

        # django-render-block should have rendered the current formset
        self.assertIn("<form", response.content.decode("utf-8"))

class TestCompleteMentorProfileView(TestCaseWithData):

    def setUp(self):
        super().setUp()
        self.today = date.today()
        self.management_form_data = {
            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,
        }

        self.url = reverse("register:complete_profile")

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    # python manage.py test --keepdb django_src.apps.register.tests.TestCompleteMentorProfileView.test_view_valid
    def test_view_valid(self):

        data = {
            # Query data
            "profile": "mentor",
            "carreer": self.computacion.name,
            "action": "create_mentor",

            # User data
            "email": "diego@gmail.com",
            "first_name": "Diego",
            "last_name": "Sánchez",
            "profile_pic": SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            ),
            "password1": "dev_123456",
            "password2": "dev_123456",

            # https://docs.djangoproject.com/en/stable/ref/forms/api/#binding-uploaded-files-to-a-form

            "voucher": SimpleUploadedFile(name="mentor_voucher.pdf", content=b"file_content", content_type="application/pdf"),

            **self.management_form_data,

            # Mentor experience data
            "form-0-name": "Full stack developer",
            "form-0-company": "Google",
            "form-0-init_year": date(2010,1,1),
            "form-0-end_year": date(2011,1,1),
            "form-0-description": "Full Stack Dev @ Google",
            "form-1-name": "Early Javascript Soy Dev",
            "form-1-company": "Apple",
            "form-1-init_year": date(2012,2,1),
            "form-1-current": True,
            "form-1-description": "Full Stack Dev @ Apple",
        }
        request = RequestFactory().post(
            path=self.url,
            data=data,
        )

        # mock htmx
        request.htmx = True


        context = profile_view.get_context(request, "create_mentor")

        # Get forms from context
        entity_form = context["entity_form"]
        exp_formset = context["exp_formset"]
        user_form = context["user_form"]

        self.assertTrue(isinstance(entity_form, MentorForm))

        # Validate forms
        self.assertTrue(user_form.is_valid(), msg=user_form.errors)
        self.assertTrue(entity_form.is_valid(), msg=entity_form.errors)
        self.assertTrue(exp_formset.is_valid(), msg=exp_formset.errors)

        # Submit the request here otherwise it will create the entities and forms above can be tested
        response = cast(HttpResponse, profile_view.complete_profile_view(request))

        self.assertEqual(response.url, reverse_lazy("register:success"))
        try:
            register_approval = RegisterApprovals.objects.get(user__email=user_form.cleaned_data["email"])
            self.assertEqual(register_approval.state, RegisterApprovalStates.WAITING)
        except RegisterApprovals.DoesNotExist:
            self.fail("RegisterApproval was not created")

        # Test that the voucher was saved
        mentor = Mentor.objects.get(user__email=user_form.cleaned_data['email'])

        self.assertEqual(mentor.experiences.count(), data["form-TOTAL_FORMS"])

        self.assertEqual(mentor.user.username, mentor.user.email)

        voucher_path = Path(mentor.voucher.path)
        self.assertTrue(voucher_path.exists())

        # Cleanup action remove the voucher
        mentor.voucher.delete()

        # Make sure the voucher was delete
        assert voucher_path.exists() == False, "Voucher was not deleted"

        # Test that the profile pic was saved
        profile_pic_path = Path(mentor.user.profile_pic.path)
        self.assertTrue(profile_pic_path.exists())

        # Cleanup action remove the profile picture file
        mentor.user.profile_pic.delete()

        # Make sure the profile picture was delete
        assert profile_pic_path.exists() == False, "Voucher was not deleted"

