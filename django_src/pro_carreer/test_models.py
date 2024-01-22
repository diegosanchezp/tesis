from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from .test_data import create_pro_carreers, create_pro_interes_themes
from wagtail.images.views.serve import generate_image_url

from django.contrib.contenttypes.models import ContentType

from wagtail.models import (
    Page,
)
from wagtail.images.models import Image

from wagtail.images.tests.utils import get_test_image_file

from django_src.apps.register.test_utils import (
    TestCaseWithData
)
from django_src.apps.register.models import (
    Mentor, Faculty, ThemeSpecProCarreer,
    CarrerSpecialization, InterestTheme,
)

# ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests
class ModelTests(TestCaseWithData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.User = get_user_model()

        cls.mentor = Mentor.objects.create(
            user=cls.mentor_user,
            carreer=cls.computacion,
        )

        # Wagtail's root page
        cls.root_page = Page.objects.get(slug='root')

        # Create some professional carreers

        pro_careers = create_pro_carreers()

        cls.fullstack_dev = pro_careers.fullstack_dev
        cls.frontend_dev = pro_careers.frontend_dev

    # ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests.test_models
    def test_models(self):
        interes_themes = create_pro_interes_themes()

        init_year=date(year=2015, month=1, day=1)

        fullstack_exp = self.fullstack_dev.career_experiences.create(
            mentor=self.mentor,
            experience="I have been working as a full stack developer for 5 years",
            rating=5,
            init_year=date(year=2015, month=1, day=1),
            end_year=init_year + timedelta(days=365*5),
        )

        self.assertEqual(self.mentor.my_career_experiences.count(), 1)
        self.assertEqual(self.fullstack_dev.career_experiences.count(), 1)

        spec_type = ContentType.objects.get_for_model(CarrerSpecialization)
        theme_type = ContentType.objects.get_for_model(InterestTheme)

        specs_pro_carreers = self.fullstack_dev.weighted_themespecs.filter(content_type=spec_type)
        self.assertGreaterEqual(specs_pro_carreers.count(), 1)
        breakpoint()

    # ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests.test_uniquness_themespec
    def test_uniquness_themespec(self):

        interes_themes = create_pro_interes_themes()
        css_frontend_dev = interes_themes.css_frontend_dev
        css_theme = interes_themes.css_theme

        # This one should fail, because it is already created
        _css_frontend_dev = ThemeSpecProCarreer.objects.create(
            weight=css_frontend_dev.weight,
            content_object=css_frontend_dev.content_object,
            object_id=css_frontend_dev.object_id,
            pro_career=css_frontend_dev.pro_career,
        )

        breakpoint()

    # ./manage.py test --keepdb django_src.pro_carreer.test_models.ModelTests.test_wagtail_image
    def test_wagtail_image(self):

        image = Image.objects.create(
            title="Test image",
            file=get_test_image_file(filename="test_rf1.png"),
        )

        self.fullstack_dev.image = image
        self.fullstack_dev.save()
        rendition = self.fullstack_dev.image.get_rendition("original")
        self.assertIsNotNone(rendition)
        self.assertIsNotNone(rendition.url)
        self.assertIsNot(rendition.url, "")

