from typing import Literal
from django.contrib import messages
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods, require_POST

from django_src.utils.webui import (
    renderMessagesAsToasts,
)
from django_src.apps.auth.views import get_profile_forms
from django_src.apps.register.models import Mentor
from django_src.mentor.utils import loggedin_and_approved
from .forms import get_MentorExperienceFormSet

from render_block import render_block_to_string


def render_exp_formset(
    exp_formset, state: Literal["INITIAL", "ADDING_NEW_EXP"], extra_context={}
):
    return render_block_to_string(
        template_name="mentor/edit_profile/index.html",
        block_name="exp_formset",
        context={
            "exp_formset": exp_formset,
            "state": state,
            **extra_context,
        },
    )


@require_POST
def save_exp(request, mentor: Mentor):
    exp_formset = get_MentorExperienceFormSet()(
        instance=mentor,
        data=request.POST,
    )

    # The form is invalid, still in the ADDING_NEW_EXP state
    state = "ADDING_NEW_EXP"

    if exp_formset.is_valid():
        exp_formset.save()
        state = "INITIAL"
        exp_formset = get_MentorExperienceFormSet()(instance=mentor)
        messages.success(request, _("Experiencia guardada"))

    html = render_exp_formset(
        exp_formset=exp_formset,
        state=state,
    )

    response = HttpResponse(html)
    renderMessagesAsToasts(request, response)
    return response


@require_POST
def reset_add_formset(request, mentor: Mentor):
    exp_formset = get_MentorExperienceFormSet()(instance=mentor)
    html = render_exp_formset(
        exp_formset=exp_formset,
        state="INITIAL",
    )
    return HttpResponse(html)


@require_POST
def add_new_exp(request, mentor: Mentor):
    """
    Validates the formsets and adds an empty form to the exp_formset
    """
    if not request.htmx:
        return HttpResponseBadRequest("This view is not meant to be called by htmx")

    # With extra = 1, we get an empty formset
    exp_formset = get_MentorExperienceFormSet(extra=1)(
        instance=mentor,
    )

    exp_formset.is_valid()

    html = render_exp_formset(
        exp_formset,
        state="ADDING_NEW_EXP",
    )

    return HttpResponse(html)


@loggedin_and_approved
@require_http_methods(["GET", "POST"])
def edit_profile_view(request):
    template_name = "mentor/edit_profile/index.html"

    user = request.user
    mentor = get_object_or_404(Mentor, user=user)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "add_new_exp":
            return add_new_exp(request, mentor)
        if action == "save_exp":
            return save_exp(request, mentor)
        if action == "reset_add_formset":
            return reset_add_formset(request, mentor)

    if request.method == "GET":
        profile_forms = get_profile_forms(user)

        # Craft a formset with the mentor experiences
        MentorExperienceFormSet = get_MentorExperienceFormSet(extra=0)
        exp_formset = MentorExperienceFormSet(
            instance=mentor,
        )

        context = {
            "mentor": mentor,
            "exp_formset": exp_formset,
            **profile_forms,
        }

        return TemplateResponse(request, template=template_name, context=context)

    return HttpResponseBadRequest("Humm no POST or GET request handled")
