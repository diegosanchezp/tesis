from django.template.response import TemplateResponse
from django_src.mentor.utils import loggedin_and_approved
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserProfileForm


def get_profile_forms(user, data=None, files=None):
    """
    Get the forms need to change the profile of the user
    """
    user_form = UserProfileForm(data=data, files=files, instance=user)
    password_form = PasswordChangeForm(user=user, data=data)
    return {
        "user_form": user_form,
        "password_form": password_form,
    }


@loggedin_and_approved
@require_POST
def change_password_view(request):
    """
    HTMX Wrapper of django.contrib.auth.views.PasswordChangeView
    """
    if not request.htmx:
        return HttpResponseBadRequest("Request not made with htmx")

    context = {**get_profile_forms(request.user, data=request.POST)}

    password_form = context["password_form"]
    if password_form.is_valid():
        password_form.save()

    return TemplateResponse(
        request, template="customauth/change_password.html", context=context
    )


# Create your views here.
@loggedin_and_approved
@require_POST
def change_profile_view(request):
    """
    Allows to change user data like first_name, last_name, password, ...
    """

    template_name = "customauth/profile_form.html"

    user = request.user
    forms = get_profile_forms(user, data=request.POST, files=request.FILES)
    user_form = forms["user_form"]

    context = {
        **forms,
    }

    if not request.htmx:
        return HttpResponseBadRequest("Request not made with htmx")

    if user_form.has_changed() and user_form.is_valid():
        user_form.save()

    return TemplateResponse(request, template=template_name, context=context)
