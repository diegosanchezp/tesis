from pathlib import Path
from datetime import datetime, date
from wagtail.rich_text import RichText
from django.contrib.auth import get_user_model
from django.conf import settings

from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup

from django_src.settings.wagtail_pages import events_index_path


class EventsData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):
        from django_src.apps.main.models import EventsIndex, EventPage

        self.EventPage = EventPage
        self.User = get_user_model()

        self.admin_user = self.User.objects.get(
            username=settings.ADMIN_USERNAME,
        )

        # The news index was created by data migration ...
        self.events_index = EventsIndex.objects.get(path=events_index_path)

        self.figma_event = EventPage(
            owner=self.admin_user,
            title="Webinar Diseño UX/UI",
            description="Aprende a utilizar Figma para construir interfaces de usuario.",
            content=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                            <p>Figma es una herramienta de diseño de interfaces dirigida principalmente a diseñadores web, UX y UI. Se destaca por ser una aplicación web que permite trabajar a través del navegador, lo que la hace accesible para una amplia gama de usuarios.</p>
                            <p>La colaboración en tiempo real es una de las fortalezas de Figma, permitiendo que varios diseñadores trabajen juntos en el mismo proyecto</p>
                         """
                        # fmt: on
                    ),
                )
            ],
            slug="webinar-diseno-ux-ui",
            first_published_at="2024-05-05T00:27:18.507Z",
            last_published_at="2024-05-05T00:27:18.507Z",
            start_date=datetime(year=2024, month=5, day=8, hour=15, minute=0),
            # end_date is not set on purpose
            place="Online"

        )
        self.iot_event = EventPage(
            owner=self.admin_user,
            title="Charla internet de las cosas",
            description="¡Este Junio se celebra la Conferencia Internacional del Internet de las Cosas en Venezuela!",
            content=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                          <p>¡Este Junio se celebra la <b>Conferencia Internacional del Internet de las Cosas</b> en Venezuela! Investigadores, líderes de la industria y entusiastas se reunirán para discutir los últimos avances y las direcciones futuras de esta tecnología que conecta miles de objetos.</p>
                         """
                        # fmt: on
                    ),
                )
            ],
            slug="charla-internet-de-las-cosas",
            first_published_at="2024-05-26T19:32:46.300Z",
            last_published_at="2024-05-28T20:16:39.592Z",
            start_date=datetime(year=2024, month=6, day=1, hour=13, minute=30),
            end_date=date(year=2024, month=6, day=8),
            place="Facultad de Ciencias, Caracas, Venezuela"
        )

    def create(self):
        self.events_index.add_child(instance=self.figma_event)
        self.events_index.add_child(instance=self.iot_event)

    def get(self):
        all_events = self.events_index.get_children()
        self.figma_event = all_events.get(slug=self.figma_event.slug)
        self.iot_event = all_events.get(slug=self.iot_event.slug)

    def delete(self):
        self.get()
        self.figma_event.delete()
        self.iot_event.delete()


# python -m django_src.apps.main.test_data.events --action create
# python -m django_src.apps.main.test_data.events --action delete
if __name__ == "__main__":
    setup(Path("."))
    args = parse_test_data_args()
    events_data = EventsData()

    if args.action == "create":
        events_data.create()
    elif args.action == "delete":
        events_data.delete()
