from django.core.paginator import Paginator
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods

from wagtail.models import Page
from render_block import render_block_to_string
from django_htmx.http import trigger_client_event

from .models import NewsPage, EventPage
from django_src.apps.register.approvals_view import get_page_number
from django_src.mentor.utils import loggedin_and_approved
from django_src.apps.main.models import EventsIndex, NewsIndex
from django_src.settings.wagtail_pages import events_index_path, news_index_path
from django_src.utils.webui import HXSwap


def get_wagtailpage_paginated(PageModel: Page, per_page: int = 6):
    """
    Get paginated queryset of wagtail pages
    """

    def get_page(
        page_number: int = 1,
        queryset=None,
        page_obj_name: str = "page_obj",
        page_number_name: str = "page_number",
        paginator_name: str = "paginator",
    ) -> dict:
        """
        Get paginated queryset of wagtail pages
        - page_obj_name: name of the page object in the context
        - page_number_name: name of the page number in the context
        """

        if queryset is None:
            queryset = PageModel.objects.all().order_by("-last_published_at")

        paginator = Paginator(
            object_list=queryset, per_page=per_page
        )  # Show 6 approvals per page.

        page_obj = paginator.get_page(page_number)

        return {
            page_obj_name: page_obj,
            page_number_name: page_number,
            paginator_name: paginator,
        }

    return get_page


get_paginated_news = get_wagtailpage_paginated(NewsPage)
get_paginated_events = get_wagtailpage_paginated(EventPage)


def evt_news_factory(section_id: str):
    context = {
        "section_id": section_id,
    }

    @loggedin_and_approved
    @require_http_methods(["GET"])
    def view(request):
        template = "main/event_news_feed_card.html"

        indexes = get_news_evt_index()

        page_number = get_page_number(request)
        if section_id == EVENT_SECTION:
            context.update(
                get_paginated_events(page_obj_name="pages", page_number=page_number)
            )
            context.update(
                {
                    "page_index": indexes["events_index"],
                }
            )
        if section_id == NEWS_SECTION:
            context.update(
                get_paginated_news(page_obj_name="pages", page_number=page_number)
            )
            context.update(
                {
                    "page_index": indexes["news_index"],
                }
            )

        response = TemplateResponse(request, template, context)
        HXSwap(response).singleSwap(
            target_element_id=f"{section_id}-load_more_btn",
            position="outerHTML",
            text_html=render_block_to_string(
                template_name="main/event_news_feed.html",
                block_name="load_more_btn",
                context=context,
            ),
        )

        return response

    return view


EVENT_SECTION = "events_feed"
get_events_view = evt_news_factory(section_id=EVENT_SECTION)

NEWS_SECTION = "news_feed"
get_more_news_view = evt_news_factory(section_id=NEWS_SECTION)


def get_news_evt_index():
    events_index = EventsIndex.objects.get(path=events_index_path)
    news_index = NewsIndex.objects.get(path=news_index_path)
    return {
        "events_index": events_index,
        "news_index": news_index,
    }
