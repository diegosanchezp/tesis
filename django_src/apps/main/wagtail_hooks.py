from django.http.request import HttpRequest
from django.urls import reverse
from wagtail.admin import widgets as wagtailadmin_widgets

from wagtail import hooks
from wagtail.models import Page, BaseViewRestriction
from wagtail.images.models import Image
from wagtail.documents.models import Document

from django_src.apps.register.models import Mentor
from django_src.business.models import Business


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


# @hooks.register("construct_page_action_menu")
# def filter_action_menu(menu_items, request, context):
#     """
#     TODO: here filter out the publish button
#     """
#     print(menu_items)


@hooks.register("construct_page_listing_buttons")
def remove_page_listing_button_item(buttons, page, user, context=None):
    # for button in buttons:
    #     if button.hook_name == 'register_page_listing_more_buttons':
    #         buttons.remove(button)
    #         break

    # print(buttons)
    # print(page)
    # print("--------------")
    pass
    # if page.is_root:
    #     buttons.pop() # removes the last 'more' dropdown button on the root page listing buttons


# @hooks.register('register_page_listing_buttons')
# def page_custom_listing_buttons(page, user, next_url=None):
#     yield wagtailadmin_widgets.ButtonWithDropdownFromHook(
#         'Acciones',
#         hook_name='my_button_dropdown_hook',
#         page=page,
#         user=user,
#         next_url=next_url,
#         priority=50
#     )
#
# @hooks.register('my_button_dropdown_hook')
# def page_custom_listing_more_buttons(page, user, next_url=None):
#     page_perms = page.permissions_for_user(user)
#     yield wagtailadmin_widgets.Button('Movea', reverse('wagtailadmin_pages:move', args=[page.id]), priority=10)
#     yield wagtailadmin_widgets.Button('Deletea', reverse('wagtailadmin_pages:delete', args=[page.id]), priority=30)
#     yield wagtailadmin_widgets.Button('Unpublish', reverse('wagtailadmin_pages:unpublish', args=[page.id]), priority=40)


@hooks.register("construct_snippet_listing_buttons")
def remove_snippet_listing_button_item(buttons, snippet, user):
    breakpoint()

    # buttons.pop()  # Removes the 'delete' button
