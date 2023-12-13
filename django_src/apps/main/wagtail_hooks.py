from django.http.request import HttpRequest

from wagtail import hooks
from wagtail.models import Page, BaseViewRestriction

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

@hooks.register("after_create_page")
def set_privacy_page_create(request, page):
    """
    Set the privacy of the page such that only logged in users can see it
    """

    # Add the login restriction to the page
    page.view_restrictions.create(restriction_type=BaseViewRestriction.LOGIN)

