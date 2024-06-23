from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.shortcuts import get_object_or_404
from django_htmx.http import trigger_client_event
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from django_src.apps.register.models import Student, Carreer
from django_src.mentor.utils import loggedin_and_approved
from django_src.student.profile.forms import EditStudentForm, ChangeSpecializationForm
from django_src.apps.auth.views import get_profile_forms
from django_src.utils.webui import close_modal, renderMessagesAsToasts
from render_block import render_block_to_string


def open_spec_modal(response, career_id: str):
    trigger_client_event(
        response=response,
        name="openSpecModal",
        params={"careerId": career_id},
    )


def get_GET_context(request):
    user = request.user
    profile_forms = get_profile_forms(user)

    student = get_object_or_404(Student, user=user)
    student_form = EditStudentForm(instance=student)
    student_form.is_valid()

    return {
        "student": student,
        "student_form": student_form,
        **profile_forms,
    }


def get_specialization_modal(request, career_id: int):
    template_name = "student/profile/modal_change_specialization.html"
    context = {}

    carreer: Carreer = get_object_or_404(
        Carreer.objects.prefetch_related("carrerspecialization_set"), pk=career_id
    )
    context["carrer"] = carreer
    context["specializations_json"] = list(
        carreer.carrerspecialization_set.all().values("name")
    )

    return TemplateResponse(request, template=template_name, context=context)


def render_spec_section(student):
    """
    Gets the html for the specialization section
    """
    response_html = render_block_to_string(
        block_name="change_specialization",
        template_name="student/profile/index.html",
        context={"student": student},
    )
    return response_html


@require_POST
@loggedin_and_approved
def change_specialization(request):
    """
    Change the specialization of the student
    """
    student = get_object_or_404(Student, user=request.user)
    form = ChangeSpecializationForm(instance=student, data=request.POST)

    if form.is_valid():
        form.save()
        messages.success(request, _("Especialización actualizada"))

        # Update the specialization section
        response_html = render_spec_section(student)
        response = HttpResponse(response_html)

        # Close the modal
        close_modal(response, "#modal-change-specialization-container")

        renderMessagesAsToasts(request, response)
        return response

    return HttpResponseBadRequest("Error changing specialization.")


@require_http_methods(["GET", "POST"])
@loggedin_and_approved
def profile_view(request):
    template_name = "student/profile/index.html"

    context = {}

    if request.method == "GET":
        context.update(get_GET_context(request))
        action = request.GET.get("action", None)
        if action == "get_specialization_modal":
            return get_specialization_modal(
                request, career_id=int(request.GET["career_id"])
            )

    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "change_specialization":
            return change_specialization(request)

    return TemplateResponse(request, template=template_name, context=context)
