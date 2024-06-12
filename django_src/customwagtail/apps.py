from django.apps.config import AppConfig
from wagtail.users.apps import WagtailUsersAppConfig


class CustomUsersAppConfig(WagtailUsersAppConfig):
    group_viewset = "django_src.customwagtail.viewsets.GroupViewSet"


class CustomWagtailConfig(AppConfig):
    name = "django_src.customwagtail"
    label = "customwagtail"
