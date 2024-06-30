from datetime import datetime
from os import environ

from django.http.response import HttpResponse
from django_src.mentor.models import MentorshipHistory, StudentMentorshipTask
from django_src.mentor.test_utils import TestCaseMentorData
from django.urls import reverse

# ./manage.py test --keepdb django_src.student.test_track_mentorship_task_view.TestTaskStateChanges
class TestTaskStateChanges(TestCaseMentorData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):

        # Login the mentor user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.student.user, password=environ["ADMIN_PASSWORD"],
        ))
        super().setUp()

    def get_mentorship_tasks(self, student):
        """
        Gets the mentorship tasks of a student
        """
        return student.mentorship_tasks.filter(task__mentorship=self.mentorship1)

    # ./manage.py test --keepdb django_src.student.test_track_mentorship_task_view.TestTaskStateChanges.test_history_created
    def test_history_created(self):
        """
        Test that the history is created
        """

        # Make all of the tasks of the student be on their initial state
        task_queryset = self.get_mentorship_tasks(self.student)
        task_queryset.update(state=StudentMentorshipTask.State.IN_PROGRESS)

        # Make all of the tasks completed except one
        self.assertIsNotNone(task_queryset)
        for task in task_queryset[:task_queryset.count() - 1]:
            task.state = StudentMentorshipTask.State.COMPLETED
            task.save()

        task_to_change = task_queryset.last()

        # Complete the mentorship by
        response = self.client.post(
            path=reverse("student:change_task_state", kwargs={"task_pk": task_to_change.pk}),
            data={"event": StudentMentorshipTask.Events.COMPLETE},
        )
        self.assertEqual(response.status_code, HttpResponse.status_code, msg=response.content.decode("utf-8"))

        # Check all student tasks are completed
        task_queryset = self.get_mentorship_tasks(self.student)
        self.assertEqual(
            task_queryset.filter(state=StudentMentorshipTask.State.COMPLETED).count(),
            task_queryset.count(),
        )

        # Check that the history was created
        self.assertTrue(
            MentorshipHistory.objects.filter(
                mentorship=self.mentorship1,
                state=MentorshipHistory.State.COMPLETED,
                student=self.student,
            ).exists(),
            msg="The mentorship history was not created"
        )

    # ./manage.py test --keepdb django_src.student.test_track_mentorship_task_view.TestTaskStateChanges.test_history_deleted
    def test_history_deleted(self):
        """
        History should be deleted if:
        - All tasks are in the completed state and task is being paused
        """
        # Create a completed history record for the mentorship
        history_obj = MentorshipHistory(
            student=self.student,
            mentorship=self.mentorship1,
            state=MentorshipHistory.State.COMPLETED,
            date=datetime.now(),
        )
        history_obj.save()

        # make all tasks be completed
        task_queryset = self.get_mentorship_tasks(self.student)
        task_queryset.update(state=StudentMentorshipTask.State.COMPLETED)

        # Transition one task to the paused state
        task_to_change = task_queryset.first()

        # Complete the mentorship by calling the view
        response = self.client.post(
            path=reverse("student:change_task_state", kwargs={"task_pk": task_to_change.pk}),
            data={"event": StudentMentorshipTask.Events.PAUSE},
        )
        self.assertEqual(response.status_code, HttpResponse.status_code, msg=response.content.decode("utf-8"))

        history_q = MentorshipHistory.objects.filter(
            student=history_obj.student,
            mentorship=history_obj.mentorship,
            state=MentorshipHistory.State.COMPLETED,
        )

        # Check that the history was deleted
        self.assertFalse(
            history_q.exists(),
        )
