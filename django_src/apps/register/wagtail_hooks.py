from .approvals_view import approvals_view

from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('approvals/', approvals_view, name='approvals'),
    ]

@hooks.register('register_admin_menu_item')
def register_calendar_menu_item():
    return MenuItem('Aprobaciones', reverse_lazy('approvals'))
