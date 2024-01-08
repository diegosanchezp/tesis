from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model

from wagtail.models import (
    Page,
)

from .models import (
    ProfessionalCarreer,
    ProCarreerIndex,
    ProCarreerExperience,

)
from django_src.apps.register.models import (
    Mentor, Faculty
)

# ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests
class ModelTests(TestCase):


    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        cls.computacion = cls.faculty.carreers.create(name="Computación")

        cls.User = get_user_model()

        cls.mentor_user = cls.User.objects.create(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
        )

        cls.mentor = Mentor.objects.create(
            user=cls.mentor_user,
            carreer=cls.computacion,
        )

    # ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests.test_models
    def test_models(self):

        # Wagtail's root page
        root_page = Page.objects.get(slug='root')

        # Create some professional carreers
        pro_career_index: ProCarreerIndex = root_page.add_child(
            instance=ProCarreerIndex(
                title="Professional Carreers",
            ),
        )

        fullstack_dev: ProfessionalCarreer = pro_career_index.add_child(
            instance=ProfessionalCarreer(
                title="Full stack Developer",
                short_description="Makes WEB GUIs & codes backend services",
            )
        )

        init_year=date(year=2015, month=1, day=1)

        fullstack_exp = fullstack_dev.career_experiences.create(
            mentor=self.mentor,
            experience="I have been working as a full stack developer for 5 years",
            rating=5,
            init_year=date(year=2015, month=1, day=1),
            end_year=init_year + timedelta(days=365*5),
        )

        self.assertEqual(self.mentor.my_career_experiences.count(), 1)
        self.assertEqual(fullstack_dev.career_experiences.count(), 1)


