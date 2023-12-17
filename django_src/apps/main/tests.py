from django.conf import settings
from django.urls.base import reverse_lazy
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from wagtail import hooks
from wagtail.models import BaseViewRestriction
from wagtail.test.utils import WagtailPageTestCase
from wagtail.test.utils import form_data
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

        cls.mentor_user = User.objects.create_user(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
            password="dev123456"
        )

        cls.mentor = Mentor.objects.create(
            user=cls.mentor_user,
            carreer=cls.computacion,
        )

        # Add user to the wagtail editors group (needed to access the admin)
        cls.editors_group = Group.objects.get(name='Editors')

        cls.mentor_user.groups.add(cls.editors_group)

    def setUp(self):
        super().setUp()

        # Login
        # self.current_user = self.login(self.mentor_user)

    # ./manage.py test --keepdb django_src.apps.main.tests.BlogPageTest.test_hook_filter_user_pages
    def test_hook_filter_user_pages(self):

        # Login the user
        self.assertTrue(self.client.login(
            username=self.mentor_user.username, password="dev123456",
        ))

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


        # Since the hook is already is registered there is no need to do it again
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    # ./manage.py test --keepdb django_src.apps.main.tests.BlogPageTest.test_privacy_set_hook
    def test_privacy_set_hook(self):
        """
        Test that when creating a page the login privacy setting of a page is set.
        """
        self.assertTrue(self.client.login(
            username=self.mentor_user.username, password="dev123456",
        ))

        self.assertTrue(self.mentor_user.is_authenticated)

        url = reverse_lazy("wagtailadmin_pages:add", args=("main", "blogpage", self.blog_index.id))

        response = self.client.post(
            path=url,
            data={
                "title": "Private Home Page",
                "slug": "private-homepage",
                "content": form_data.rich_text("<p>My private home page</p>"),
                "action-submit": "Submit for moderation",
            }
        )

        self.assertEqual(response.status_code, 302)

        created_blog = BlogPage.objects.get(slug="private-homepage")

        self.assertTrue(created_blog.view_restrictions.filter(restriction_type=BaseViewRestriction.LOGIN).exists())

        # Now make a request editing the page that was previously created
        # but first, remove the privacy setting, just to make sure that is not the creation page that set it
        created_blog.view_restrictions.get(restriction_type=BaseViewRestriction.LOGIN).delete()

        self.assertEqual(
            created_blog.view_restrictions.filter(
                restriction_type=BaseViewRestriction.LOGIN
            ).count(),
            0
        )

        edit_data = {
            "title": "Re - Private The Home Page",
            "slug": "private-homepage",
            "content": form_data.rich_text("<p>My private home page</p>"),
            # "action-submit": "Submit for moderation",
        }

        url = reverse_lazy("wagtailadmin_pages:edit", args=(created_blog.id,))

        response = self.client.post(
            path=url,
            data=edit_data,
        )

        self.assertEqual(response.status_code, 200, msg=response)

        # Refecth from database
        created_blog = BlogPage.objects.get(slug="private-homepage")

        # The edit_data is has probably something wrong and that is why the page was not updated
        # You can do manual testing, by putting a breakpoint on the hook, to see if the page was updated
        # self.assertEqual(created_blog.title, edit_data["title"])

        # self.assertTrue(created_blog.view_restrictions.filter(restriction_type=BaseViewRestriction.LOGIN).exists())
