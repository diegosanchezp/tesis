from os import environ

from .test_utils import TestCaseMentorData
from .test_data import MentorshipData

from django.urls.base import reverse_lazy

# ./manage.py test --keepdb django_src.mentor.test_edit_mentorship.TestEditMentorshipView
class TestEditMentorshipView(TestCaseMentorData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        mentorship_data = MentorshipData(cls.mentor_data)

        mentorship_data.create()
        mentorship_data.get()

        cls.mentorship1 = mentorship_data.mentorship1
        cls.m1_task1 = mentorship_data.m1_task1

    def setUp(self):
        super().setUp()

        self.mentor = self.mentorship1.mentor

        # Login the mentor user
        self.assertTrue(self.client.login(
            username=self.mentor.user, password=environ["ADMIN_PASSWORD"],
        ))
    # ./manage.py test --keepdb django_src.mentor.test_edit_mentorship.TestEditMentorshipView.test_edit_mentorship
    def test_edit_mentorship(self):
        data = {
            'action': 'edit',
            'form-INITIAL_FORMS': '1',
            'form-MAX_NUM_FORMS': '1000',
            'form-MIN_NUM_FORMS': '0',
            'form-TOTAL_FORMS': '2',
            # Mentorship data
            'mentor': '11',
            'name': 'Actualizacion de Creación de curriculum',
            # First mentorship task
            'form-0-id': self.m1_task1.pk,
            'form-0-name': 'Escribir las 10 cosas que mas te gustan de tu carrera!',
            # Empty mentorship task
            'form-1-id': '',
            'form-1-name': '',
        }

        response = self.client.post(
            path=reverse_lazy("mentor:edit_mentorship", kwargs={"mentorship_pk": self.mentorship1.pk}),
            data=data,
            headers={"HX-Request": "true"},
        )

        response_html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)

        # Refetch task from db
        mentorship1 = self.mentor.mentorships.get(pk=self.mentorship1.pk)
        m1_task1 = mentorship1.tasks.get(pk=self.m1_task1.pk)

        # Check if the task was updated
        self.assertEqual(m1_task1.name, data['form-0-name'])
        self.assertIn(m1_task1.name, response_html)

        self.assertEqual(mentorship1.name, data['name'])
        self.assertIn(mentorship1.name, response_html)

