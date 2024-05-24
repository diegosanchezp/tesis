from django import template
from django_src.settings.wagtail_pages import pro_carreer_index_path
from django_src.pro_carreer.models import ProCarreerIndex

register = template.Library()

# https://adamj.eu/tech/2023/03/23/django-context-processors-database-queries/
@register.inclusion_tag("pro_carreer/index_link.html")
def pro_carrer_index_link():
    pro_carreer_index = ProCarreerIndex.objects.get(path=pro_carreer_index_path)

    return {
        "pro_carreer_index": pro_carreer_index
    }
