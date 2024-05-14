from django.views.decorators.http import require_http_methods

from .utils import get_mentor, loggedin_and_approved
from django.template.response import TemplateResponse
from django_src.apps.main.models import EventsIndex, NewsIndex
from django_src.apps.main.news_event_views import (
    get_paginated_events,
    get_paginated_news,
    NEWS_SECTION,
    EVENT_SECTION,
)


@require_http_methods(["GET"])
@loggedin_and_approved
def landing_view(request):
    template = "mentor/landing.html"
    mentor = get_mentor(request.user.get_username())
    events_index = EventsIndex.objects.first()
    news_index = NewsIndex.objects.first()

    context = {
        "mentor": mentor,
        "EVENT_SECTION": EVENT_SECTION,
        "NEWS_SECTION": NEWS_SECTION,
        "events_index": events_index,
        "news_index": news_index,
        **get_paginated_news(
            page_obj_name="news",
            page_number_name="news_page_number",
            paginator_name="news_paginator",
        ),
        **get_paginated_events(
            page_obj_name="events",
            page_number_name="events_page_number",
            paginator_name="events_paginator",
        ),
    }

    return TemplateResponse(request, template, context)
