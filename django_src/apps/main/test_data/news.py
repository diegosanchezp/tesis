from pathlib import Path
from wagtail.rich_text import RichText
from django.contrib.auth import get_user_model
from django.conf import settings

from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup

from django_src.settings.wagtail_pages import news_index_path


class NewsData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):
        from django_src.apps.main.models import NewsIndex, NewsPage

        self.NewsPage = NewsPage
        self.User = get_user_model()

        self.admin_user = self.User.objects.get(
            username=settings.ADMIN_USERNAME,
        )

        # The news index was created by data migration ...
        self.news_index = NewsIndex.objects.get(path=news_index_path)

        self.news_aporte = NewsPage(
            owner=self.admin_user,
            title="La Asociación de Egresados recibe más de $5000 en aportes.",
            description="Se ha alcanzado la meta de recauda de $5000. El dinero se invertirá en proyectos de Investigación y Desarrollo",
            content=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                        <p>La Asociación ha logrado recaudar. Entre los proyectos de Investigación y Desarrollo en los que se invertiran los fondos estan:</p>
                        <ul>
                            <li>LLM</li>
                        </ul>
                        """
                        # fmt: on
                    ),
                )
            ],
            slug="la-asociacion-de-egresados-recibe-mas-de-5000-en-aportes",
            first_published_at="2024-05-02T00:27:18.507Z",
            last_published_at="2024-05-02T00:27:18.507Z",
        )

    def create(self):
        self.news_index.add_child(instance=self.news_aporte)

    def get(self):
        all_news = self.news_index.get_children()
        self.news_aporte = all_news.get(slug=self.news_aporte.slug)

    def delete(self):
        self.get()
        self.news_aporte.delete()


# python -m django_src.apps.main.test_data.news --action create
# python -m django_src.apps.main.test_data.news --action delete
if __name__ == "__main__":
    setup(Path("."))
    args = parse_test_data_args()
    news_data = NewsData()

    if args.action == "create":
        news_data.create()
    elif args.action == "delete":
        news_data.delete()
