from .approvals_view import approvals_view

from django.utils.translation import gettext_lazy as _
from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem


@hooks.register("register_admin_urls")
def register_admin_urls():
    return [
        path("approvals/", approvals_view, name="approvals"),
    ]


menu_aprobaciones = MenuItem(label=_("Aprobaciones"), url=reverse_lazy("approvals"), icon_name="tasks", order=1)


@hooks.register("register_admin_menu_item")
def register_menu_aprobaciones():
    return menu_aprobaciones


@hooks.register("construct_main_menu")
def hide_approvals_for_mentors(request, menu_items):
    """
    Approvals menu should not be shown to mentors or businesses
    """
    # Delete the Approvals MenuItem from the menu_items list, if the user is a mentor or business or teacher
    if request.user.is_mentor or request.user.is_business or request.user.is_professor:
        menu_items[:] = [
            item for item in menu_items if item.label != menu_aprobaciones.label
        ]
