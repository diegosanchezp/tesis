from django.contrib import messages
from django.http.response import HttpResponseForbidden
from django.urls.base import reverse_lazy
from django_htmx.http import trigger_client_event

from django_src.utils.webui import renderMessagesAsToasts

from .models import Mentorship, StudentMentorshipTask, MentorshipRequest, MentorshipHistory
from .utils import get_mentor, loggedin_and_approved
from .forms import MentorshipReqFilterForm
from .landing_view import paginate_mentorship_request, get_filter_mentorship_requests, FILTER_MENTORSHIP_REQUEST, render_mentorship_req_table, FILTER_MENTORSHIP_REQUEST
from django_src.apps.register.models import Mentor, Student
from django_src.utils import get_page_number

from render_block import render_block_to_string

from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.db import models
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

def get_detail_view_context(mentor: Mentor, mentorship: Mentorship):

    tasks_number = mentorship.tasks.count()

    students_info = StudentMentorshipTask.objects.filter(
        task__mentorship=mentorship
    ).values(
        "student__pk",
        "student__user__first_name",
        "student__user__last_name",
    ).annotate(
        tasks_num=models.Value(tasks_number), # Number of tasks, calculated from the task template
        tasks_completed=models.Count("task", filter=models.Q(state=StudentMentorshipTask.State.COMPLETED)),
    ).annotate(
        is_completed=models.Case(
            models.When(tasks_completed=models.F("tasks_num"), then=True),
            default=False,
            output_field=models.BooleanField()
        )
    ).order_by("is_completed")

    context = {
        "mentor": mentor,
        "mentorship": mentorship,
        "students_info": students_info,
        "FILTER_MENTORSHIP_REQUEST": FILTER_MENTORSHIP_REQUEST,
        "tasks": mentorship.tasks.all(),
    }

    return context

def render_mentorship_info(mentor: Mentor, mentorship: Mentorship):
    """
    Renders the mentorship info
    """
    template_name = 'mentor/mentorship_detail.html'
    context = get_detail_view_context(mentor, mentorship)
    return render_block_to_string(template_name, "mentorship_info", context)

def get_student_table_html(context):
    return render_block_to_string(
        template_name=mentorship_detail_template,
        block_name="mentorship_students_table",
        context=context,
    )
@require_http_methods(["GET"])
def update_student_table(request, context):
    students_table_html = get_student_table_html(context)
    return HttpResponse(students_table_html)

mentorship_detail_template = 'mentor/mentorship_detail.html'
@require_http_methods(["GET", "POST"])
@loggedin_and_approved
def mentorship_detail_view(request, mentorship_pk: int):
    """
    Detail view for a mentorship
    """

    template_name = mentorship_detail_template

    mentorship = get_object_or_404(Mentorship.objects.prefetch_related("tasks"), pk=mentorship_pk)
    is_admin = request.user.is_superuser
    is_mentor = request.user.is_mentor
    mentorship_mentor = mentorship.mentor

    if is_mentor:
        mentor = get_mentor(request.user.username, prefetch_related="mentorships")
        if mentorship_mentor != mentor:
            return HttpResponseBadRequest("No autorizado para ver la mentoría")
    elif is_admin:
        mentor = mentorship_mentor
    else:
        return HttpResponseBadRequest("No autorizado para ver la mentoría")


    action = request.GET.get("action")
    page_number = get_page_number(request)
    context = get_detail_view_context(mentor, mentorship)
    context.update(
        breadcrumbs=[
            {"name": "Mis mentorías", "href": reverse_lazy("mentor:my_mentorships")},
            {"name": mentorship.name },
        ]
    )

    # Mentorship request filters
    filter_form = MentorshipReqFilterForm(data=request.GET)
    filter_form.is_valid()
    context["filter_form"] = filter_form

    student_name = filter_form.cleaned_data["student_name"]
    state = filter_form.cleaned_data["state"]
    mentorship_requests = get_filter_mentorship_requests(mentor, student_name, state)
    mentorship_requests = mentorship_requests.filter(mentorship=mentorship)

    # Add the paginated mentorship requests to the context
    context.update(
        paginate_mentorship_request(
            mentorship_requests,
            page_number=page_number,
        )
    )

    if request.htmx:
        if action == "render_mentorship_info":
            form_html = render_mentorship_info(mentor, mentorship)
            return HttpResponse(form_html)
        if action == FILTER_MENTORSHIP_REQUEST:
            return render_mentorship_req_table(template_name, context)
        if action == "update_student_table":
            return update_student_table(request, context)
        else:
            HttpResponseForbidden("Invalid action")


    response = TemplateResponse(request, template_name, context)

    return response

bool_map = {
    "true": True,
    "false": False,
    "False": False,
    "True": True,
}
@require_http_methods(["GET"])
@loggedin_and_approved
def student_info_view(request, mentorship_request_pk: int):
    """
    Render brief info of a student on a modal
    For detail view
    """
    if not request.htmx:
        return HttpResponseBadRequest('request not made with htmx')

    with_mentorship_name = bool(
        bool_map.get(request.GET.get("with_mentorship_name", False))
    )
    mentorship_request = get_object_or_404(MentorshipRequest, pk=mentorship_request_pk)
    student = mentorship_request.student

    return TemplateResponse(request, "mentor/student_info_modal.html", {
        "student": student,
        "mentorship_request": mentorship_request,
        "MentorshipRequest": MentorshipRequest,
        "with_mentorship_name": with_mentorship_name,
    })


@require_http_methods(["POST"])
def delete_student_from_mentorship(request, mentorship_pk: int, student_pk: int):
    """
    """
    # Unit tests: django_src/mentor/test_edit_mentorship.py

    mentorship = get_object_or_404(Mentorship, pk=mentorship_pk)
    student = get_object_or_404(Student, pk=student_pk)
    is_mentor = request.user.is_mentor
    if not (is_mentor or request.user.is_superuser):
        return HttpResponseBadRequest("Only admins or mentors are allowed")
    mentor = request.user.mentor

    # First check that the mentorship is owned by the mentor
    if mentorship.mentor != mentor:
        return HttpResponseBadRequest("You can't delete a student from a mentorship that isn't yours")

    # delete the tasks of the student
    StudentMentorshipTask.objects.filter(student=student, task__mentorship=mentorship).delete()

    # delete the mentorship history
    MentorshipHistory.objects.filter(student=student, mentorship=mentorship).delete()

    # delete the mentorship request
    MentorshipRequest.objects.filter(mentorship=mentorship, student=student).delete()

    context = get_detail_view_context(mentor, mentorship)

    # Update the table of student overview
    student_table_html = get_student_table_html(context)

    response = HttpResponse(student_table_html)
    # Update the table of mentorship requests
    trigger_client_event(
        response=response,
        name="update_req_table",
    )
    messages.success(request, "Estudiante eliminado de la mentoría")
    renderMessagesAsToasts(request, response)
    # Update the table of requests
    return response

