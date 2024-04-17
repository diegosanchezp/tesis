from .test_utils import TestCaseMentorData

# ./manage.py test --keepdb django_src.mentor.test_mentorship_list_view.TestListMentorshipView
class TestListMentorshipView(TestCaseMentorData):

    @classmethod
    def setUpTestData(cls):

    def setUp(self):
        super().setUp()
        # Login the student user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.student.user, password=environ["ADMIN_PASSWORD"],
        ))
    # ./manage.py test --keepdb django_src.mentor.test_mentorship_list_view.TestListMentorshipView.test_list_menthorships
    def test_list_menthorships(self):
        
        self.client.get(
        )

