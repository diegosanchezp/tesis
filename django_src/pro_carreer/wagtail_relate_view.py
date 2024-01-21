from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from django_src.apps.register.models import (
    CarrerSpecialization, InterestTheme, ThemeSpecProCarreer
)

from .models import ( ProfessionalCarreer )
from .forms import ( ActionForm, ThemeSpecRelateForm, RelateActions, DeleteThemeSpecRelateForm )

model_names_classes = {
    CarrerSpecialization.__name__: CarrerSpecialization,
    InterestTheme.__name__: InterestTheme,
}

def get_default_context(request, pro_career: ProfessionalCarreer):

    context = {
        "pro_career": pro_career,
        "RelateActions": RelateActions
    }

    return context

def create_spec_relation(request, pro_career: ProfessionalCarreer, model_type: str):
    """
    View for making the relation between specialization with
    professional career
    """

    model = model_names_classes[model_type]

    context = get_default_context(request, pro_career)

    theme_spec_form = ThemeSpecRelateForm(model=model, data=request.POST)

    context["theme_spec_form"] = theme_spec_form

    if theme_spec_form.is_valid():

        weight = theme_spec_form.cleaned_data["weight"]
        theme_specialization: CarrerSpecialization | InterestTheme = theme_spec_form.cleaned_data["theme_spec"]

        try:
            theme_spec_procareer = theme_specialization.pro_carreers_match.create(
                weight=weight, pro_career=pro_career,
            )
            context["theme_spec"] = theme_spec_procareer
        except IntegrityError:
            error_msg = "Ya está creada la relación con " # Leave trailing space at the end
            # If theme_specialization is of type CarrerSpecialization
            if isinstance(theme_specialization, CarrerSpecialization):
                error_msg += f"la especialización {theme_specialization.name}, elige otra"
            else:
                error_msg += f"el tema de interés {theme_specialization.name}, elige otro"

            theme_spec_form.add_error(None, error_msg)
            # go to render form

        # render form
        return TemplateResponse(request, "pro_carreer/spec_procareer_match.html", context)

    # todo return html with the form errors rendereed for invalid case


def delete_themespec(request, pro_career: ProfessionalCarreer, model_type: str):
    """
    Deletes the relation between theme or specialization with professional career
    """

    context = get_default_context(request, pro_career)

    model = model_names_classes[model_type]
    form = DeleteThemeSpecRelateForm(model=model,data=request.POST)

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
        context["spec_form"] = ThemeSpecRelateForm(model=CarrerSpecialization)
        context["theme_form"] = ThemeSpecRelateForm(model=InterestTheme)

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
        model_type = action_form.cleaned_data["model_type"]

        if action == RelateActions.RELATE_THEME_SPEC.value:
            return create_spec_relation(request, pro_career, model_type=model_type)

        if action == RelateActions.DELETE_THEME_SPEC.value:
            return delete_themespec(request, pro_career, model_type=model_type)

    return HttpResponseNotAllowed(
        [
            request.method,
        ]
    )
    # context["theme_form"] =

