from django.urls import reverse_lazy
from django.http.request import QueryDict
from django.contrib import messages
from django.forms import BaseForm

def get_page_number(request):
    """
    Gets the page number from the request object.
    """
    page_number: str | int | None = request.GET.get("page") or request.POST.get("page")

    if page_number is None:
        page_number = 1
    elif isinstance(page_number, str):
        page_number = int(page_number)

    return page_number


def remove_index_publish_permission(page_permission_tester, user):
    """
    Removes the publish permission from a wagtail page that is considered an index.
    """

    if not getattr(page_permission_tester, "permissions", False):
        return page_permission_tester

    if (
        user.is_mentor or user.is_business
    ) and "publish" in page_permission_tester.permissions:
        page_permission_tester.permissions.remove("publish")

    return page_permission_tester


def formdata_to_querystring(form, extra: dict = {}):

    query_dict = QueryDict(mutable=True)
    if not form.is_valid():
        return ""
    for key, value in form.cleaned_data.items():
        if value:
            query_dict[key] = value
    query_dict.update(extra)
    return query_dict.urlencode()

def get_home_page_link(user):
    if not user.is_authenticated:
        return 
    if user.is_superuser:
        return reverse_lazy("wagtailadmin_home")
    if user.is_business:
        return reverse_lazy("business:landing")
    if user.is_mentor:
        return reverse_lazy("mentor:landing")
    if user.is_student:
        return reverse_lazy("pro_carreer:student_carreer_match")

def render_field_errors_as_messages(request, form: BaseForm, field_name: str):
    """
    Renders the errors of a field as toast messages
    """
    if not form.errors:
        return

    if field_name in form.errors:
        for error_msg in form.errors[field_name]:
            messages.error(request,message=error_msg)

