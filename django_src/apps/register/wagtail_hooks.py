from .approvals_view import approvals_view

from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('approvals/', approvals_view, name='approvals'),
    ]

menu_aprobaciones = MenuItem(label='Aprobaciones', url=reverse_lazy('approvals'))

@hooks.register('register_admin_menu_item')
def register_calendar_menu_item():
    return menu_aprobaciones

@hooks.register('construct_main_menu')
def hide_approvals_for_mentors(request, menu_items):
    """
    Approvals menu should not be shown to mentors
    """
    # Delete the Approvals MenuItem from the menu_items list, if the user is a mentor
    if request.user.is_mentor:
        menu_items[:] = [item for item in menu_items if item.label != menu_aprobaciones.label]
