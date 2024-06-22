from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from django_htmx.http import trigger_client_event
from django_src.apps.register.models import Faculty, Carreer, Student, Mentor
from render_block import render_block_to_string
from django_src.apps.register.forms import QueryForm, StudentForm, MentorForm
from django_src.mentor.utils import loggedin_and_approved
from django_src.utils import hxSwap, renderMessagesAsToasts
from django.utils.translation import gettext_lazy as _


def get_career_context(request):
    facultys = Faculty.objects.prefetch_related("carreers").order_by("name")

    entity_type = get_entity_type(request.user)
    carreer = None
    if entity_type == QueryForm.ESTUDIANTE:
        entity = Student.objects.get(user__pk=request.user.pk)
        carreer = entity.carreer
    if entity_type == QueryForm.MENTOR:
        entity = Mentor.objects.get(user__pk=request.user.pk)
        carreer = entity.carreer

    # faculty_num is used to determine the number of columns of the grid of facultys
    faculty_num = facultys.count()

    return {
        "facultys": facultys,
        "faculty_num": faculty_num,
        "carreer": carreer,
        "carreer_name": carreer.name,
    }


def close_modal_rpc(response: HttpResponse):

    trigger_client_event(
        response=response,
        name="closeModal",
        params={"modalTargetId": "#career-selector-modal"},
    )


def update_career_name(response, entity):
    """
    Update the career name in the profile edit UI
    """

    hxSwap(
        response,
        target_element_id="career-form",
        position="outerHTML",
        text_html=render_to_string(
            template_name="main/career/change_career.html",
            context={
                "entity": entity,
            },
        ),
    )


@require_POST
@loggedin_and_approved
def change_career(request):
    entity_type = get_entity_type(request.user)
    entity_id = request.user.pk

    query_form = QueryForm(
        data={"profile": entity_type, "carreer": request.POST.get("carreer")}
    )

    if query_form.is_valid():
        profile = query_form.cleaned_data["profile"]
        carreer = query_form.cleaned_data["carreer"]

        if profile == QueryForm.ESTUDIANTE:
            student = Student.objects.get(user__pk=entity_id)
            student.carreer = carreer
            student.save()
            response = HttpResponse("Carrera cambiada exitosamente")

            close_modal_rpc(response)

            update_career_name(response=response, entity=student)

            # Show a success message
            messages.success(request, "Carrera cambiada exitosamente")

            # TODO: If there are any specializations in the career, tell the student to select one
            if carreer.carrerspecialization_set.count() > 0:
                messages.info(
                    request, message=_("Por favor selecciona una especialización")
                )
                pass

            renderMessagesAsToasts(request, response)

            return response

        if query_form.cleaned_data["profile"] == QueryForm.MENTOR:
            mentor = Mentor.objects.get(user__pk=entity_id)
            mentor.carreer = carreer
            response = HttpResponse("Carrera cambiada exitosamente")
            close_modal_rpc(response)
            return response

    response = HttpResponseBadRequest("Error al cambiar la carrera")
    return response


@require_GET
def search_careers(request):
    search_key = request.GET["search"]
    context = {**get_career_context(request)}

    facultys = context["facultys"]

    # Filter the queryset with the given search key
    if search_key != "":
        # First get the carrers that matches the search key
        carreers = Carreer.objects.filter(name__icontains=search_key)
        # Then get the facultys that have the carrers
        facultys = facultys.filter(carreers__in=carreers)

        # Update context
        context["facultys"] = facultys
        context["faculty_num"] = facultys.count()

    results_html = render_block_to_string(
        template_name="components/career_selector.html",
        block_name="carrer_form",
        context=context,
    )

    return HttpResponse(results_html)


def get_entity_type(user):
    if user.is_student:
        return QueryForm.ESTUDIANTE

    if user.is_mentor:
        return QueryForm.MENTOR

    return None


@require_GET
@loggedin_and_approved
def get_careers_modal(request):
    template_name = "components/modal_career_selector.html"

    context = {
        **get_career_context(request),
    }

    return TemplateResponse(request, template=template_name, context=context)
