from django.urls import path
from .news_event_views import get_more_news_view, get_events_view
from .career_views import get_careers_modal, search_careers, change_career

urlpatterns = [
    path("news_feed/", get_more_news_view, name="news_feed"),
    path("events_feed/", get_events_view, name="events_feed"),
    path("get_careers_modal/", get_careers_modal, name="get_careers_modal"),
    path("search_careers/", search_careers, name="search_careers"),
    path("change_career/", change_career, name="change_career"),
]
