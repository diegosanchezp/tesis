from django_src.apps.register.test_utils import TestCaseWithData
from django_src.apps.register.test_data.mentors import MentorData

from django_src.pro_carreer.test_data import create_pro_carreers

class TestCaseMentorData(TestCaseWithData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        pro_carreers = create_pro_carreers()

        cls.frontend_dev = pro_carreers.frontend_dev
        cls.fullstack_dev = pro_carreers.fullstack_dev

        cls.mentor_data = MentorData()

        cls.mentor_data.create(cls.computacion, cls.fullstack_dev)
        cls.mentor_data.get()
        cls.mentor1 = cls.mentor_data.mentor1
        cls.mentor2 = cls.mentor_data.mentor2
