from os import environ

from django.http.response import HttpResponse, HttpResponseForbidden
from django.test.client import RequestFactory

from .models import Mentorship, MentorshipRequest, StudentMentorshipTask
from .forms import MentorshipForm
from .utils import loggedin_and_approved
from .test_utils import TestCaseMentorData
from django.urls.base import reverse_lazy

# ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestUtils
class TestUtils(TestCaseMentorData):
    """
    Test the utilty functions
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestUtils.test_login_approved_decorator
    def test_login_approved_decorator(self):
        """
        Test that the login_and_approved decorator works as expected
        """
        @loggedin_and_approved
        def test_func(request):
            return HttpResponse("OK")

        # Create an instance of a GET request.
        request = self.factory.get("")

        # You can simulate a logged-in user by setting request.user manually.

        # Test that the user is approved
        request.user = self.mentor1.user
        response = test_func(request)
        self.assertEqual(response.status_code, HttpResponse.status_code)

        # Test that the user is NOT approved
        request.user = self.student_data.unapproved_student.user
        response = test_func(request)

        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)


# ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestCreateMentorshipView
class TestCreateMentorshipView(TestCaseMentorData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()


    def setUp(self):

        super().setUp()
        # Login the mentor user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.mentor1.user, password=environ["ADMIN_PASSWORD"],
        ))

        self.url = reverse_lazy("mentor:create_mentorship")

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestCreateMentorshipView.test_add_task_formset
    def test_add_task_formset(self):
        """
        Test that a third task can be added
        """
        response = self.client.post(
            path=self.url,
            data={
                "action": "validate_add_tasks",

                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 0,
                "form-MIN_NUM_FORMS": 0,
                "form-MAX_NUM_FORMS": 1000,

                "form-0-name": "Escribir  10 cosas que mas te gustan de tu carrra.", # name of a task
            },
            headers={
                # mocks htmx
                "HX-Request": "true"
            },
        )
        self.assertEqual(response.status_code, 200)

        response_html = response.content.decode()
        self.assertIsNotNone(response_html)

        # Check that form-TOTAL_FORMS is equal to two
        self.assertIn(f"name=\"form-TOTAL_FORMS\" value=\"2\"", response_html)
        print(response_html)

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestCreateMentorshipView.test_create_mentorship
    def test_create_mentorship(self):

        mentorship_name = "Creación de curriculum!"

        data = {
            "name": mentorship_name, # name of the mentorship
            "mentor": self.mentor1.pk,
            "action": "create",

            "form-TOTAL_FORMS": 2,
            "form-INITIAL_FORMS": 0,
            "form-MIN_NUM_FORMS": 0,
            "form-MAX_NUM_FORMS": 1000,

            "form-0-name": "Escribir  10 cosas que mas te gustan de tu carrra.", # name of a task
            "form-1-name": "Escribe los 3 lenguajes de programación que más te gustan.",
        }
        self.client.post(
            path=self.url,
            data=data,
        )

        try:
            mentorship = Mentorship.objects.get(name=mentorship_name)
        except Mentorship.DoesNotExist:
            self.fail(msg="Mentorship not found")

        self.assertEqual(mentorship.tasks.count(),data["form-TOTAL_FORMS"])
    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestCreateMentorshipView.test_render_forms
    def test_render_forms(self):
        form = MentorshipForm()


# ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestRequestMentorshipView
class TestRequestMentorshipView(TestCaseMentorData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.mentorship = cls.mentorship_data.mentorship1

    def setUp(self):

        super().setUp()

        # Login the student user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.student.user, password=environ["ADMIN_PASSWORD"],
        ))

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestRequestMentorshipView.test_make_mentorship_request
    def test_make_mentorship_request(self):

        # Delete mentorship request other unique error will be raised
        self.mentorship.mentorship_requests.filter(student=self.student).delete()

        response = self.client.post(
            path=reverse_lazy("mentor:request_mentorship", kwargs={"mentorship_pk": self.mentorship.pk})
        )

        self.assertEqual(response.status_code, 200)
        try:
            mentorship_req = MentorshipRequest.objects.get(mentorship=self.mentorship)
        except MentorshipRequest.DoesNotExist:
            self.fail(msg="Mentorship request not created")

        self.assertEqual(mentorship_req.student, self.student)
        self.assertEqual(mentorship_req.status, MentorshipRequest.State.REQUESTED)

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestRequestMentorshipView.test_list_menthorships
    def test_list_menthorships(self):

        # Add another mentorship that the student hasn't requested
        self.mentorship2 = Mentorship(
            name="Microservices mentorship",
            mentor=self.mentor1,
        ).save()

        path=reverse_lazy(
            "mentor:mentorias", kwargs={"username": self.mentor1.user.username}
        )

        response = self.client.get(
            path=path
        )
        self.assertEqual(response.status_code, 200)
        response_html = response.content.decode()
        self.assertIsNotNone(response_html)

        print(response_html)


# ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestChangeMentorshipStatusView
class TestChangeMentorshipStatusView(TestCaseMentorData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        mentorship_data = cls.mentorship_data


        cls.mentorship1 = mentorship_data.mentorship1

        cls.m_task1 = mentorship_data.m1_task1
        cls.m_task2 = mentorship_data.m1_task2
        cls.m_task3 = mentorship_data.m1_task3

        # Set the mentorship request status to requested
        cls.mentorship_request = cls.mentorship_data.mentorship1.mentorship_requests.first()
        cls.mentorship_request.status = MentorshipRequest.State.REQUESTED
        cls.mentorship_request.save()

        # For invalid cases
        cls.mentorship2 = Mentorship(
            name="Ayuda vocacional",
            mentor=cls.mentor2,
        )

        cls.mentorship2.save()
        cls.mentorship_request2 = cls.mentorship2.mentorship_requests.create(
            student=cls.student,
        )

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestChangeMentorshipStatusView.test_accept_mentorship_status
    def test_accept_mentorship_status(self):
        # -----
        # Case: mentor approves mentorship
        # -----

        # Login the mentor user
        self.assertTrue(self.client.login(
            username=self.mentor1.user, password=environ["ADMIN_PASSWORD"],
        ))

        response = self.client.post(
            path=reverse_lazy("mentor:change_mentorship_status", kwargs={"mentorship_req_pk": self.mentorship_request.pk}),
            data={
                "action": MentorshipRequest.Events.ACCEPT,
            }
        )

        self.assertEqual(response.status_code, 200, response.content.decode())

        # refetch mentorship_request
        re_mentorship_request = MentorshipRequest.objects.get(pk=self.mentorship_request.pk)

        self.assertEqual(re_mentorship_request.status, MentorshipRequest.State.ACCEPTED)

        for task in re_mentorship_request.mentorship.tasks.all():
            self.assertTrue(StudentMentorshipTask.objects.filter(student=re_mentorship_request.student, task=task).exists())

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestChangeMentorshipStatusView.test_change_mentorship_status_invalid
    def test_change_mentorship_status_invalid(self):

        # -----
        # Case: mentor can't change mentorship that he did not create
        # Mentor 2 didn't create self.mentorship
        # -----


        # Login the mentor user
        self.assertTrue(self.client.login(
            username=self.mentor2.user, password=environ["ADMIN_PASSWORD"],
        ))

        response = self.client.post(
            path=reverse_lazy("mentor:change_mentorship_status", kwargs={"mentorship_req_pk": self.mentorship_request.pk}),
            data={
                "action": MentorshipRequest.Events.REJECT,
            }
        )

        self.assertEqual(response.status_code, 400)
        response_html = response.content.decode()
        self.assertIsNotNone(response_html)
        print(response_html)

# ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestMentorshipDetailView
class TestMentorshipDetailView(TestCaseMentorData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.mentorship1 = cls.mentorship_data.mentorship1

    def setUp(self):
        super().setUp()

        self.mentor = self.mentorship1.mentor

        # Login the mentor user
        self.assertTrue(self.client.login(
            username=self.mentor.user, password=environ["ADMIN_PASSWORD"],
        ))

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestMentorshipDetailView.test_detail_view
    def test_detail_view(self):
        # make the last of the tasks of the mentorship completed
        m_task = self.student.mentorship_tasks.filter(task__mentorship=self.mentorship1).last()
        if m_task:
            m_task.state = StudentMentorshipTask.State.COMPLETED
            m_task.save()

        response = self.client.get(
            path=reverse_lazy("mentor:mentorship_detail", kwargs={"mentorship_pk": self.mentorship1.pk})
        )

        self.assertEqual(response.status_code, 200)

        students = response.context["students_info"]
        student_mentorship_info = students.get(student=self.student)

        print(student_mentorship_info)
        student_tasks = self.student.mentorship_tasks.filter(task__mentorship=self.mentorship1)

        self.assertEqual(student_mentorship_info["is_completed"], False)
        self.assertEqual(student_mentorship_info["tasks_completed"], student_tasks.filter(state=StudentMentorshipTask.State.COMPLETED).count())

        self.assertEqual(student_mentorship_info["tasks_num"], student_tasks.count())

    # ./manage.py test --keepdb django_src.mentor.test_mentorship_view.TestMentorshipDetailView.test_get_edit_form
    def test_get_edit_form(self):

        response = self.client.get(
            path=reverse_lazy("mentor:edit_mentorship", kwargs={"mentorship_pk": self.mentorship1.pk}),
            data={
                "action": "get_edit_form",
            },
            headers={"HX-Request": "true"},
        )

        self.assertEqual(response.status_code, 200)

        response_html = response.content.decode()
        self.assertIsNotNone(response_html)
        print(response_html)

