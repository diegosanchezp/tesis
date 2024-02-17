from datetime import date, timedelta
from django_src.apps.register.test_utils import TestCaseWithData
from django.urls.base import reverse_lazy
from django.template.loader import render_to_string

from os import environ

from .test_data import (
    create_pro_carreers
)

from .forms import ProCareerExpForm
from . import experience_view
from django_src.apps.register.test_data.mentors import MentorData

class TestExperienceView(TestCaseWithData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        pro_carreers = create_pro_carreers()

        cls.frontend_dev = pro_carreers.frontend_dev
        cls.fullstack_dev = pro_carreers.fullstack_dev
        cls.pro_career_index = pro_carreers.pro_career_index

        mentor_data = MentorData()
        mentor_data.create(cls.computacion, cls.fullstack_dev)
        mentor_data.get()

        cls.mentor_user = mentor_data.mentor1_user
        cls.mentor1 = mentor_data.mentor1

    def setUp(self):

        super().setUp()
        self.url = self.fullstack_dev.get_url()

        # Login the mentor user, need it to populate request.user
        self.assertTrue(self.client.login(
            username=self.mentor_user, password=environ["ADMIN_PASSWORD"],
        ))

    # ./manage.py test --keepdb django_src.pro_carreer.test_experience_view.TestExperienceView.test_get_experiences
    def test_get_experiences(self):

        response = self.client.get(
            path="/profesiones/full-stack-developer/",
            data={
                "tab": "experiencias",
            }
        )

        request = response.wsgi_request

        context = experience_view.get_experiences(request, page=self.fullstack_dev)

        experiences = context["experiences"]
        mentor_experience = context["mentor_experience"]
        self.assertIsNotNone(experiences)
        self.assertGreaterEqual(experiences.count(), 0)

        self.assertIsNotNone(mentor_experience)
        self.assertEqual(mentor_experience.mentor, self.mentor1)

        # Mentor experience should not be in the experiences queryset
        self.assertFalse(experiences.contains(mentor_experience))


    # ./manage.py test --keepdb django_src.pro_carreer.test_experience_view.TestExperienceView.test_create_experience_invalid
    def test_create_experience_invalid(self):

        # Simulate creation of an invalid form
        init_year = date(year=2010, month=1, day=1)

        form = ProCareerExpForm(data={
            "experience": "",
            "rating": 3,
            "company": "Uber",
            "init_year": init_year + timedelta(days=365*5),
            "end_year": init_year,
        })

        self.assertFalse(form.is_valid())

        html = render_to_string(
            template_name="pro_carreer/mentor_exp.html",
            context={"form": form, "state": "adding",}
        )

        print(html)

    # ./manage.py test --keepdb django_src.pro_carreer.test_experience_view.TestExperienceView.test_render_distribution
    def test_render_distribution(self):

        response = self.client.get(
            path="/profesiones/full-stack-developer/",
            data={
                "tab": "experiencias",
            }
        )

        request = response.wsgi_request

        response = experience_view.render_distribution(request, pro_career=self.fullstack_dev)

        res_html = response.content.decode("utf-8")

        print(res_html)
