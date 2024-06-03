from django_src.apps.register.test_utils import TestCaseWithData
from django_src.apps.register.models import Carreer


# ./manage.py test --keepdb django_src.business.directory.students_view_tests.StudentDirectoryViewTests
class StudentDirectoryViewTests(TestCaseWithData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    # ./manage.py test --keepdb django_src.business.directory.students_view_tests.StudentDirectoryViewTests.test_students_paginated
    def test_students_paginated(self):
        """ """

        page = self.computacion.paginated_students()
        self.assertIsNotNone(page)
        print(page)
