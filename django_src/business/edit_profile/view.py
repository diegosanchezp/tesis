from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods, require_POST
from django_src.apps.auth.views import get_profile_forms
from django_src.business.edit_profile.forms import EditBusinessForm
from django_src.business.models import Business
from django_src.mentor.utils import loggedin_and_approved
from django.shortcuts import get_object_or_404
from render_block import render_block_to_string
from django.contrib import messages
from django_src.utils.webui import renderMessagesAsToasts
from django.utils.translation import gettext_lazy as _

template_name = "business/edit_profile/index.html"


@require_POST
def update_business(request, business: Business):

    business_form = EditBusinessForm(request.POST, instance=business)

    if business_form.is_valid():
        business = business_form.save()
        business_form = EditBusinessForm(instance=business)
        messages.success(request, _("Empresa actualizada"))

    html = render_block_to_string(
        template_name=template_name,
        block_name="business_form",
        context={
            "business_form": business_form,
        },
    )

    response = HttpResponse(html)
    renderMessagesAsToasts(request, response)
    return response


@loggedin_and_approved
@require_http_methods(["GET", "POST"])
def business_edit_profile_view(request):
    user = request.user

    business = get_object_or_404(Business, user=request.user)

    if request.method == "POST":
        action = request.POST.get("action")
        if not action:
            return HttpResponseBadRequest("No action provided")

        if action == "update_business":
            return update_business(request, business)

    if request.method == "GET":

        profile_forms = get_profile_forms(user)
        business_form = EditBusinessForm(instance=business)

        context = {
            "business_form": business_form,
            **profile_forms,
        }
        return TemplateResponse(request, template_name, context=context)

    return HttpResponseBadRequest("Humm no POST or GET request handled")
