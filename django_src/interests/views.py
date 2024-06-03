from typing import Any
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http.response import HttpResponse

from render_block import render_block_to_string

from django_src.apps.register.models import InterestTheme
from django_src.mentor.utils import loggedin_and_approved
from django_src.utils import get_page_number


def get_interest_queryset(order: str = "name"):
    return InterestTheme.objects.order_by(order)


def get_interest_theme_page(page_number: int, interests: QuerySet | None = None):

    if not interests:
        interests = get_interest_queryset()
    paginator = Paginator(
        object_list=interests,
        # Show 4 themes per page.
        per_page=8,
    )

    page_obj = paginator.get_page(page_number)
    return page_obj


@loggedin_and_approved
def get_interest_theme_page_view(request, extra_context: dict[str, Any] = {}):
    """
    Used in interest theme selector component

    This view is not meant to be used in a urls.py file. It extends other views to add the interest theme selector component functionality.
    """

    page_number = get_page_number(request)
    interest_themes = get_interest_queryset()
    interest_themes_page = get_interest_theme_page(page_number, interest_themes)

    context = {
        "interest_themes": interest_themes_page,
    }
    context.update(extra_context)

    html = render_block_to_string(
        template_name="components/interests_selector.html",
        block_name="interest_list",
        context=context,
    )

    return HttpResponse(html)
