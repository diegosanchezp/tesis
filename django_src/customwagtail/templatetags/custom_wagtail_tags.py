from django.conf import settings
from django import template
from django.templatetags.static import static
from urllib.parse import urljoin

register = template.Library()

@register.simple_tag
def custom_notification_static(path):
    """
    Variant of the {% static %}` tag for use in notification emails - tries to form
    a full URL using WAGTAILADMIN_BASE_URL if the static URL isn't already a full URL.
    """
    base_url: str = settings.BASE_URL
    return urljoin(base_url, static(path))
