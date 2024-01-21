from wagtail import hooks
from django.urls import path
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from wagtail.admin import widgets as wagtailadmin_widgets
from .wagtail_relate_view import relate_theme_spec_view
from .models import (
    ProfessionalCarreer,
)

@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        path('relate_theme_spec/<int:pk_pro_career>', relate_theme_spec_view, name='relate_theme_spec'),
    ]

@hooks.register('register_page_listing_more_buttons')
def page_listing_buttons(page, user, next_url=None):

    pro_career_type = ContentType.objects.get_for_model(ProfessionalCarreer)

    if page.content_type == pro_career_type:
        yield wagtailadmin_widgets.PageListingButton(
            _('Relacionar tema o especialización'),
            reverse_lazy('relate_theme_spec', kwargs={"pk_pro_career": page.pk}),
            priority=10
        )
