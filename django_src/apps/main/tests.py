from django.conf import settings
from django.urls.base import reverse_lazy
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from wagtail import hooks
from wagtail.models import BaseViewRestriction
from wagtail.test.utils import WagtailPageTestCase
from wagtail.models import Page

from .models import BlogPage, BlogIndex
from django_src.apps.register.models import Mentor, Faculty

class BlogPageTest(WagtailPageTestCase):
    """
    See django_src/apps/main/migrations/0003_wagtail_setup.py to see
    how data is defined
    """

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.admin_user = User.objects.get(
            username=settings.ADMIN_USERNAME,
        )

        cls.faculty = Faculty.objects.get(
            name="Ciencias",
        )

        cls.computacion = cls.faculty.carreers.get(name="Computación")

        cls.root_page = Page.objects.get(slug='root')
        cls.blog_index = BlogIndex.objects.get(slug="blogs", owner=cls.admin_user)

        cls.mentor_user = cls.create_user(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
            password="password",
        )

        cls.mentor = Mentor.objects.create(
            user=cls.mentor_user,
            carreer=cls.computacion,
        )


    def setUp(self):
        super().setUp()

        # Login
        self.current_user = self.login(self.mentor_user)

    # ./manage.py test --keepdb django_src.apps.main.tests.BlogPageTest.test_hook_filter_user_pages
    def test_hook_filter_user_pages(self):

        # Get the url of the view that list all the pages
        url = reverse_lazy("wagtailadmin_explore_root")

        # Create a blog page with restrictions
        self.blog_page = BlogPage(
            owner=self.mentor_user,
            title="Blog Page",
            slug="blog-page",
            content="My first Blog !!!",
        )

        # Assign the blog pages as a child of the root
        blog_child = self.blog_index.add_child(instance=self.blog_page)

        # Create login restriction for this page
        blog_child.view_restrictions.create(
            restriction_type=BaseViewRestriction.LOGIN,
        )

        self.assertEquals(blog_child.view_restrictions.count(), 1)

        # Add user to the wagtail editors group (needed to access the admin)
        editors_group = Group.objects.get(name='Editors')

        self.current_user.groups.add(editors_group)

        # Since the hook is already is registered there is no need to do it again
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
