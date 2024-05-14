from pathlib import Path
from wagtail.rich_text import RichText
from django_src.apps.register.test_data.mentors import MentorData
from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup


class MentorBlogData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self, mentor_data: MentorData):
        from django_src.apps.main.models import BlogPage, BlogIndex

        self.BlogPage = BlogPage
        self.BlogIndex = BlogIndex

        self.mentor_data = mentor_data

        # Create two blogs for the mentors
        self.mentor1 = mentor_data.mentor1

        # The blog index was created my migration 0003_wagtail_setup.py
        self.blog_index = BlogIndex.objects.get(slug="blogs")
        self.blog_mentor1 = self.BlogPage(
            owner=self.mentor_data.mentor1_user,
            title="Blog Mentor 1",
            slug="blog-mentor-1",
            content=[
                (
                    "paragraph",
                    RichText(
                        "<h2>Mi primer blog</h2>"
                        "<p>Aquí escribiré muchas cosas, tales como</p>"
                        "<ul>"
                        "<li>Cosa 1</li>"
                        "<li><s>Cosa 2</s></li>"
                        "</ul>"
                    ),
                ),
                ("paragraph", RichText("<blockquote>Parrafo Nuevo</blockquote>")),
            ],
        )

    def create(self):
        self.mentor_data.get()
        self.blog_mentor1.owner = self.mentor_data.mentor1_user
        self.blog_mentor1 = self.blog_index.add_child(instance=self.blog_mentor1)

    def get(self):
        self.blog_mentor1 = self.BlogPage.objects.get(slug=self.blog_mentor1.slug)

    def delete(self):
        self.get()
        self.blog_mentor1.delete()


# python -m django_src.mentor.test_blog_data --action create
# python -m django_src.mentor.test_blog_data --action delete
if __name__ == "__main__":
    setup(Path("."))
    args = parse_test_data_args()

    blog_data = MentorBlogData(mentor_data=MentorData())
    if args.action == "create":
        blog_data.create()
    elif args.action == "delete":
        blog_data.delete()
