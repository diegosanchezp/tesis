from django import forms
from wagtail.users.views.groups import (
    GroupViewSet as WagtailGroupViewSet,
    EditView,
    get_permission_panel_classes,
)
from wagtail.users.forms import (
    BaseGroupPagePermissionFormSet,
    PagePermissionsForm,
    GroupPagePermissionFormSet,
)
from wagtail.models import PAGE_PERMISSION_TYPES
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission

UNPUBLISH_PAGE_CODE = "unpublish_page"
MY_PAGE_PERMISSION_TYPES = PAGE_PERMISSION_TYPES + [
    (UNPUBLISH_PAGE_CODE, _("Unpublish"), _("UnPublish")),
]

PAGE_PERMISSION_CODENAMES = [identifier for identifier, *_ in MY_PAGE_PERMISSION_TYPES]


class MyPagePermissionsForm(PagePermissionsForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Refetch the queryset so that the custom permissions appear in the field
        self.fields["permissions"].queryset = Permission.objects.filter(
            content_type__app_label="wagtailcore",
            content_type__model="page",
            codename__in=PAGE_PERMISSION_CODENAMES,
        ).order_by("codename")


class MyBaseGroupPagePermissionFormSet(BaseGroupPagePermissionFormSet):
    permission_types = MY_PAGE_PERMISSION_TYPES


MyGroupPagePermissionFormSet = forms.formset_factory(
    MyPagePermissionsForm,
    formset=MyBaseGroupPagePermissionFormSet,
    extra=0,
    can_delete=True,
)


class MyEditView(EditView):
    """
    Modified EditView to use our custom GroupPagePermissionFormSet
    The purpose of this is to add a new permission type to the formset
    """

    def get_permission_panel_forms(self, *args, **kwargs):
        permission_panels = super().get_permission_panel_forms(*args, **kwargs)

        # Replace the original PagePermissionsFormFormSet with our custom one
        for idx, panel_class in enumerate(permission_panels):
            if isinstance(panel_class, GroupPagePermissionFormSet):
                permission_panels[idx] = MyGroupPagePermissionFormSet(
                    **self.get_permission_panel_form_kwargs(
                        MyGroupPagePermissionFormSet
                    )
                )

        return permission_panels


class GroupViewSet(WagtailGroupViewSet):
    edit_view_class = MyEditView
