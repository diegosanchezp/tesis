from django.urls import path
from .news_event_views import get_more_news_view, get_events_view

urlpatterns = [
    path("news_feed/",get_more_news_view, name="news_feed"),
    path("events_feed/",get_events_view, name="events_feed"),
]
