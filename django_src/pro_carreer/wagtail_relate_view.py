from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from django_src.apps.register.models import (
    CarrerSpecialization, InterestTheme, ThemeSpecProCarreer
)

from .models import ( ProfessionalCarreer )
from .forms import ( ActionForm, SpecRelateForm, ThemeRelateForm, RelateActions, DeleteSpecRelateForm )

def get_default_context(request, pro_career: ProfessionalCarreer):

    context = {
        "pro_career": pro_career,
        "RelateActions": RelateActions
    }

    return context

def create_spec_relation(request, pro_career: ProfessionalCarreer):
    """
    View for making the relation between specialization with
    professional career
    """

    context = get_default_context(request, pro_career)

    spec_form = SpecRelateForm(request.POST)

    context["spec_form"] = spec_form

    if spec_form.is_valid():

        weight = spec_form.cleaned_data["weight"]
        specialization = spec_form.cleaned_data["specialization"]

        spec_procareer = specialization.pro_carreers_match.create(
            weight=weight, pro_career=pro_career,
        )

        context["spec_procareer"] = spec_procareer

        return TemplateResponse(request, "pro_carreer/spec_procareer_match.html", context)

    # todo return html with the form errors rendereed for invalid case


def delete_themespec(request, pro_career: ProfessionalCarreer):
    """
    Deletes the relation between theme or specialization with professional career
    """

    context = get_default_context(request, pro_career)

    form = DeleteSpecRelateForm(request.POST)

    if form.is_valid():
        weighted_spec: ThemeSpecProCarreer = form.cleaned_data["weighted_spec"]
        weighted_spec.delete()

        # Since we are deleting we dont need to html
        return HttpResponse("ok")

    # Invalid case, I guess, I should render the invalid form message ?
    return HttpResponse("Not found", status=404)
    # pro_career is assumed  


    # try:
    #     spec_match = pro_career.weighted_themespecs.get(content_type=spec_type, pk=weighted_spec_pk)
    # except ThemeSpecProCarreer.DoesNotExist:


def create_theme_relation(request, pro_career: ProfessionalCarreer):
    """
    View for making the relation between theme with
    professional career
    """

    theme_form = ThemeRelateForm(request.POST)

    context = {}
    context["theme_form"] = theme_form

    if theme_form.is_valid():
        theme = theme_form.cleaned_data["theme"]
        wheight = theme_form.cleaned_data["weight"]

        theme.pro_carreers_match.create(
                weight=wheight, pro_career=pro_career,
        )

        # todo return html

def delete_theme_relation(request, pro_career: ProfessionalCarreer):
    # TODO
    pass

@require_http_methods(["GET", "POST"])
def relate_theme_spec_view(request, pk_pro_career: int):
    """
    View for making the relation between themes/specialization with
    professional career
    """

    template_name = "pro_carreer/wagtail_relate_view.html"

    spec_type = ContentType.objects.get_for_model(CarrerSpecialization)
    theme_type = ContentType.objects.get_for_model(InterestTheme)

    # Get the professional career
    pro_career = get_object_or_404(ProfessionalCarreer, pk=pk_pro_career)
    context = get_default_context(request, pro_career)

    if request.method == "GET":
        context["spec_form"] = SpecRelateForm()
        context["theme_form"] = ThemeRelateForm()

        # TODO: optimize the querys with a select related
        # TODO: order by weight
        context["specs_pro_carreers"] = pro_career.weighted_themespecs.filter(content_type=spec_type)
        context["themes_pro_carreers"] = pro_career.weighted_themespecs.filter(content_type=theme_type)

        return TemplateResponse(request, template_name, context)

    if request.method == "POST" and request.htmx:

        action_form = ActionForm(request.POST)

        if not action_form.is_valid():
            context["action_form"] = action_form
            return TemplateResponse(request, template_name, context)

        action = action_form.cleaned_data["action"]

        if action == RelateActions.RELATE_SPECIALIZATION.value:
            return create_spec_relation(request, pro_career)

        if action == RelateActions.DELETE_SPECIALIZATION.value:
            return delete_themespec(request, pro_career)

        if action == RelateActions.RELATE_THEME.value:
            return create_theme_relation(request, pro_career)

    return HttpResponseNotAllowed(
        [
            request.method,
        ]
    )
    # context["theme_form"] =

