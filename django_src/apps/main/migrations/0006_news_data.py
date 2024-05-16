# Generated by Django 5.0.4 on 2024-05-02 21:37

from django.db import migrations
from django.conf import settings

from django.apps.registry import Apps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django_src.settings.wagtail_pages import (
    home_page_path,
    news_index_path,
    events_index_path,
)


def create_news_events_data(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):

    # get_user_model doesn't works in data migrations because it sets required_ready to False
    User = apps.get_model(settings.AUTH_USER_MODEL)
    NewsIndex = apps.get_model("main", "NewsIndex")
    EventsIndex = apps.get_model("main", "EventsIndex")
    ContentType = apps.get_model("contenttypes.ContentType")
    HomePage = apps.get_model("main", model_name="HomePage")

    # Admin is Created by 0002_setup_admin
    admin = User.objects.get(username=settings.ADMIN_USERNAME)

    newsindex_content_type, created = ContentType.objects.get_or_create(
        model="newsindex", app_label="main"
    )

    eventsindex_content_type, created = ContentType.objects.get_or_create(
        model="eventsindex", app_label="main"
    )

    # Home page was created in previous migrations
    home_page = HomePage.objects.get(path=home_page_path)

    # Create NewsIndex and EventsIndex
    NewsIndex.objects.create(
        owner=admin,
        content_type=newsindex_content_type,
        live=True,
        title="Noticias",
        locale=home_page.locale,
        slug="noticias",
        url_path="/noticias/",
        path=news_index_path,
        depth=3,
    )

    EventsIndex.objects.create(
        owner=admin,
        content_type=eventsindex_content_type,
        live=True,
        title="Eventos",
        locale=home_page.locale,
        slug="eventos",
        url_path="/eventos/",
        path=events_index_path,
        depth=3,
    )


def remove_news_events_data(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):

    # Page = apps.get_model("wagtailcore", model_name="Page")
    NewsIndex = apps.get_model("main", "NewsIndex")
    EventsIndex = apps.get_model("main", "EventsIndex")

    NewsPage = apps.get_model("main", "NewsPage")
    EventPage = apps.get_model("main", "EventPage")

    news_index = NewsIndex.objects.get(path=news_index_path)
    news_index.delete()
    # delete all news pages the index .delete() method doesn't delete its children
    # so we have to do it manually
    NewsPage.objects.all().delete()

    events_index = EventsIndex.objects.get(path=events_index_path)
    events_index.delete()
    # delete all events pages the index .delete() method doesn't delete its children
    # so we have to do it manually
    EventPage.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0005_eventsindex_newsindex_eventpage_newspage"),
    ]

    operations = [
        migrations.RunPython(create_news_events_data, remove_news_events_data),
    ]