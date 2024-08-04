from django.http.request import HttpRequest
from django.urls import path, reverse_lazy

from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.models import Page, BaseViewRestriction
from wagtail.images.models import Image
from wagtail.documents.models import Document

from django_src.apps.register.models import Mentor
from django_src.business.models import Business

from django.urls import path

from django_src.customwagtail.interest_themes.view import crud_interest


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path(
            "crud_interest_themes", view=crud_interest, name="cms_interest_themes_crud"
        ),
    ]


menu_interest_themes = MenuItem(
    label="Temas de interés", url=reverse_lazy("cms_interest_themes_crud")
)


@hooks.register("register_admin_menu_item")
def register_menus():
    return menu_interest_themes


@hooks.register("construct_explorer_page_queryset")
def filter_user_pages(parent_page: Page, pages, request: HttpRequest):
    """
    Get the pages that the user has created,
    applicable to mentors and business only
    """
    if not (
        Mentor.objects.filter(user=request.user).exists()
        or Business.objects.filter(user=request.user).exists()
    ):
        return pages

    return pages.filter(owner=request.user)


@hooks.register("after_create_page")
@hooks.register("after_edit_page")
def set_privacy_page_create(request, page):
    """
    Set the privacy of the page such that only logged in users can see it
    """
    if not (
        Mentor.objects.filter(user=request.user).exists()
        or Business.objects.filter(user=request.user).exists()
    ):
        return page

    # Add the login restriction to the page
    page.view_restrictions.create(restriction_type=BaseViewRestriction.LOGIN)
    return page


@hooks.register("construct_document_chooser_queryset")
def list_my_documents(documents, request):
    """
    For mentors: list the documents that I've uploaded when a document chooser is opened
    """
    if not Mentor.objects.filter(user=request.user).exists():
        return documents
    return Document.objects.filter(uploaded_by_user=request.user)


@hooks.register("construct_image_chooser_queryset")
def list_my_images(images, request):
    """
    For mentors: list the images that I've uploaded when an image chooser is opened
    """

    if not Mentor.objects.filter(user=request.user).exists():
        return images

    return Image.objects.filter(uploaded_by_user=request.user)


@hooks.register("construct_page_chooser_queryset")
def show_my_pages_only(pages, request):
    """
    Only show own pages if I'm a mentor or if I'm a business
    """

    if not (
        Mentor.objects.filter(user=request.user).exists()
        or Business.objects.filter(user=request.user).exists()
    ):
        return pages
    return pages.filter(owner=request.user)

@hooks.register("construct_main_menu")
def hide_menus_for_users(request, menu_items):
    """
    Hide CMS menus that should only be available for admins and other types of superusers
    """

    if request.user.is_superuser or request.user.is_staff:
        pass
    else:
        menu_items[:] = [
            item for item in menu_items if item.label != menu_interest_themes.label
        ]

