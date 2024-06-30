from django_src.mentor.test_utils import TestCaseMentorData
from .my_mentorships_view import get_student_mentorships

# ./manage.py test --keepdb django_src.student.mentorships.tests.TestMyMentorshipView
class TestMyMentorshipView(TestCaseMentorData):

    # ./manage.py test --keepdb django_src.student.mentorships.tests.TestMyMentorshipView.test_get_student_mentorships
    def test_get_student_mentorships(self):
        student_mentorships = get_student_mentorships(self.student)
        self.assertTrue(student_mentorships.exists())
        student_info = student_mentorships.first()
        self.assertIsNotNone(student_info.task_todo)
        self.assertIsNotNone(student_info.is_completed)
