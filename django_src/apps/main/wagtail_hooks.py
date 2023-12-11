from django.http.request import HttpRequest

from wagtail import hooks
from wagtail.models import Page

from django_src.apps.register.models import Mentor

@hooks.register("construct_explorer_page_queryset")
def filter_user_pages(parent_page: Page, pages, request: HttpRequest):
    """
    Get the pages that the user has created,
    applicable to mentors only
    """
    if not Mentor.objects.filter(user=request.user).exists():
        return pages

    return pages.filter(owner=request.user)
