from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls.base import reverse
from render_block.base import render_block_to_string
from django_src.apps.register.views import step_urls
from .forms import (
    BusinessForm,
    BusinessUserCreationForm,
    ActionForm,
    BusinessRegisterAction,
)
from django.views.decorators.http import require_http_methods
from django_src.apps.register.complete_profile_view import create_user, create_approval


def create_business(user, business_form: BusinessForm):

    # Create an instance of the business object but don't save it to DB,
    # because it doesn't have a related user yet
    business = business_form.save(commit=False)

    # Relate the user instance to the business
    business.user = user

    # Finally save to database
    business.save()

    return business


@require_http_methods(["GET", "POST"])
def register_business_view(request):
    template_name = "business/register/index.html"
    context = {
        "step_urls": step_urls,
        "BusinessRegisterAction": BusinessRegisterAction,
    }

    if request.method == "POST":
        action_form = ActionForm(request.POST)
        action_form.is_valid()
        action = action_form.cleaned_data["action"]

        business_form = BusinessForm(request.POST)
        user_form = BusinessUserCreationForm(data=request.POST, files=request.FILES)

        if action == BusinessRegisterAction.REGISTER:
            # Combine the form data of the two forms
            # forms_are_valid = business_form.is_valid() or user_form.is_valid()
            context.update(business_form=business_form, user_form=user_form)

            if user_form.is_valid():
                user = create_user(user_form)
                if business_form.is_valid():
                    business = create_business(user, business_form)
                    create_approval(user, business)
                    return HttpResponseRedirect(redirect_to=reverse("register:success"))

    if request.method == "GET":
        business_form = BusinessForm()
        user_form = BusinessUserCreationForm()

    context.update(
        {
            "business_form": business_form,
            "user_form": user_form,
        }
    )

    return TemplateResponse(request, template_name, context=context)
