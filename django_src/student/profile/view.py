from django.http.response import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from django_src.utils import render_field_errors_as_messages
from django_src.apps.register.models import Student, Carreer, StudentInterest
from django_src.mentor.utils import loggedin_and_approved
from django_src.student.profile.forms import (
    ChangeSpecializationForm,
    ChangeInterestForm,
    get_add_interest_queryset,
    AddInterestForm,
)
from django_src.apps.auth.views import get_profile_forms
from django_src.utils.webui import HXSwap, close_modal, renderMessagesAsToasts
from render_block import render_block_to_string

from django_htmx.http import trigger_client_event
from django_src.interests.views import (
    get_interest_theme_page_view,
    get_interest_theme_page,
)


# Look down for profile_view, is the main entry point


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

    # Get interest that are still not yet added by the student
    interests_to_add_queryset = get_add_interest_queryset(student)
    interests_to_add_page = get_interest_theme_page(
        page_number=1, interests=interests_to_add_queryset
    )

    interest_form = ChangeInterestForm(instance=student)
    return {
        "student": student,
        **profile_forms,
        "interest_form": interest_form,
        "interests_to_add": interests_to_add_page,
    }


def get_specialization_modal(request, career_id: int):
    template_name = "student/profile/modal_change_specialization.html"
    context = {
        "student": get_object_or_404(Student, user=request.user),
    }

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


interest_page_view_base_context = {
    "action_name": "paginate_student_interests",
    "input_name": "interests",
    "list_id": "interests-to-add-list",
}


def get_actual_interest_html(
    student: Student, interest_form: ChangeInterestForm | None = None
):
    return render_block_to_string(
        template_name="student/profile/index.html",
        block_name="actual_interests",
        context={
            "student": student,
            "interest_form": interest_form,
        },
    )


def get_other_interest_html(request, student: Student):
    response = get_interest_theme_page_view(
        request,
        interest_queryset=get_add_interest_queryset(student),
        extra_context={
            **interest_page_view_base_context,
        },
    )
    return response


@require_POST
def delete_student_interests(request):
    """
    Bulk delete interest of a student
    """
    student = get_object_or_404(Student, user=request.user)

    interest_form = ChangeInterestForm(instance=student, data=request.POST)

    if interest_form.is_valid():
        interests_to_delete = interest_form.cleaned_data["interests"]
        student_interests = StudentInterest.objects.filter(
            student=student, interest__in=interests_to_delete
        )
        student_interests.delete()

        messages.success(request, _("Intereses eliminados"))

    actual_interests_html = get_actual_interest_html(student, interest_form)
    response = HttpResponse(actual_interests_html)

    if interest_form.is_valid():

        # Update the other interests, that can be added

        response_other_interest = get_other_interest_html(request, student)
        other_interest_html = response_other_interest.content.decode("utf-8")
        # breakpoint()

        HXSwap(response).singleSwap(
            target_element_id="interests-to-add-list",
            position="innerHTML",
            text_html=other_interest_html,
        )

    renderMessagesAsToasts(request, response)

    return response


@require_POST
def add_interest_to_student(request):
    """
    Add interests to a student
    """
    student = get_object_or_404(Student, user=request.user)
    interest_add_form = AddInterestForm(data=request.POST, instance=student)

    if interest_add_form.is_valid():
        interests_to_add = interest_add_form.cleaned_data["interests"]
        student.interests.add(*interests_to_add)

        response = get_other_interest_html(request, student)

        # Update the actual interest
        HXSwap(response).singleSwap(
            target_element_id="actual-interests",
            position="outerHTML",
            text_html=get_actual_interest_html(student=student),
        )

        messages.success(request, _("Intereses añadidos"))
        renderMessagesAsToasts(request, response)

        return response

    response = HttpResponseBadRequest("Error adding interests.")
    render_field_errors_as_messages(request, form=interest_add_form, field_name='interests')
    renderMessagesAsToasts(request,response)
    return response


@require_GET
def paginate_student_interests(request):
    """ """
    student = get_object_or_404(Student, user=request.user)
    interests = get_add_interest_queryset(student)

    return get_interest_theme_page_view(
        request=request,
        interest_queryset=interests,
        extra_context={
            **interest_page_view_base_context,
        },
    )


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
        if action == "paginate_student_interests":
            return paginate_student_interests(request)

    if request.method == "POST":
        action = request.POST.get("action", None)
        if action == "change_specialization":
            return change_specialization(request)
        if action == "delete_student_interests":
            return delete_student_interests(request)
        if action == "add_interest_to_student":
            return add_interest_to_student(request)

    return TemplateResponse(request, template=template_name, context=context)
