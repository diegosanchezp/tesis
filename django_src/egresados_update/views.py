from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods

from django_src.utils.webui import renderMessagesAsToasts
from .forms import (
    CedulaForm,
    EgresadoUpdateValidate,
    EgresadosUpdateForm,
    GETActionTypes,
    GETActionTypesForm,
)
from .models import EgresadosData
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from render_block import render_block_to_string

egresados_index_template = "egresados_update/index.html"


@require_http_methods(["GET", "POST"])
def root_view(request):
    """
    Main view, finds and updates an Egresado's data
    """

    if request.method == "POST":

        context = {}

        ci_form = EgresadoUpdateValidate(data=request.POST)
        context["ci_form"] = ci_form
        context["view_state"] = "updating_data"

        if ci_form.is_valid():
            egresado_instance = ci_form.instance
            egresados_form = EgresadosUpdateForm(
                data=request.POST, instance=egresado_instance
            )
            context["egresados_form"] = egresados_form

            if egresados_form.is_valid():
                egresados_form.save()
                context["view_state"] = "edit_success"
                if request.htmx:
                    response = render_updating_data(context)
                    messages.success(request, _("Datos del egresado actualizados"))
                    renderMessagesAsToasts(request, response)
                    return response
            else:
                if request.htmx:
                    response = render_updating_data(context)
                    messages.error(request, _("Han habido errores al ingresar datos"))
                    renderMessagesAsToasts(request, response)
                    return response

        return TemplateResponse(request, egresados_index_template, context)

    if request.method == "GET":

        GET_action_types_form = GETActionTypesForm(data=request.GET)
        cedula_form = CedulaForm()
        view_state = "default"

        context = {
            # "egresados_form": egresados_form,
            "cedula_form": cedula_form,
            "view_state": view_state,
            "GET_action_types_form": GET_action_types_form,
            "GETActionTypes": GETActionTypes,
        }

        if GET_action_types_form.is_valid():
            action = GET_action_types_form.cleaned_data["action"]
            cedula_form = CedulaForm(data=request.GET)
            context["cedula_form"] = cedula_form

            cedula_form_is_valid = cedula_form.is_valid()

            # This is for model forms leaving it here just in case we use one back again.
            # we do consider the form valid if the cedula exists
            # if not cedula_form_is_valid:
            #     all_errors = cedula_form.errors.get("__all__", None)
            #     if all_errors:
            #         cedula_form_is_valid = "ya existe." in  all_errors[0]

            # Check if the egresado exist on db withs its cedula
            if action == GETActionTypes.CONSULTAR.value and cedula_form_is_valid:
                cleaned_data = cedula_form.cleaned_data
                cedula = cleaned_data["cedula"]
                prefijo_cedula = cleaned_data["prefijo_cedula"]

                try:
                    egresado_data = EgresadosData.objects.get(
                        cedula=cedula, prefijo_cedula=prefijo_cedula
                    )
                    context["view_state"] = "updating_data"
                    context["egresado_data"] = egresado_data
                    context["egresados_form"] = EgresadosUpdateForm(
                        instance=egresado_data
                    )

                    if request.htmx:
                        return render_updating_data(context)
                except EgresadosData.DoesNotExist:
                    cedula_form.add_error(
                        None,
                        error=ValidationError(
                            _(
                                "No encontramos datos registrados con la cédula: %(prefijo_cedula)s %(cedula)s, intenta de nuevo."
                            ),
                            params={"cedula": cedula, "prefijo_cedula": prefijo_cedula},
                            code="invalid",
                        ),
                    )

                    if request.htmx:
                        html = render_block_to_string(
                            template_name=egresados_index_template,
                            block_name="default_state",
                            context=context,
                        )
                        response = HttpResponse(html)
                        # messages.err(request, _("Aplicado a la oferta de trabajo"))
                        # renderMessagesAsToasts(request, response)
                        return response
            else:
                if request.htmx:
                    return render_updating_data(context)

        return TemplateResponse(request, egresados_index_template, context)


def render_updating_data(context):
    """
    Renders "updating_data" block section.
    """
    html = render_block_to_string(
        template_name=egresados_index_template,
        block_name="updating_data",
        context=context,
    )
    response = HttpResponse(html)
    return response
