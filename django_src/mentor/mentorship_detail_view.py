from .models import Mentorship, StudentMentorshipTask, MentorshipRequest
from django_src.apps.register.models import Mentor, Student
from .utils import get_mentor, is_approved, get_page_number

from render_block import render_block_to_string

from django.db.models.query import QuerySet
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.db import models
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

def get_detail_view_context(mentor: Mentor, mentorship: Mentorship):

    tasks_number = mentorship.tasks.count()

    students_info = StudentMentorshipTask.objects.filter(
        task__mentorship=mentorship
    ).values(
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

def paginate_mentorship_request(request, queryset: QuerySet[MentorshipRequest]):
    paginator = Paginator(object_list=queryset, per_page=1)  # Change to Show 10 mentorship requests.
    page_number = get_page_number(request)
    paginated_m_requests = paginator.get_page(page_number)

    return {
        "mentorship_requests": paginated_m_requests,
        "page_number": page_number,
    }

@login_required
@require_http_methods(["GET"])
@is_approved
def mentorship_detail_view(request, mentorship_pk: int):
    """
    Detail view for a mentorship
    """

    template_name = 'mentor/mentorship_detail.html'

    mentor = get_mentor(request.user.username, prefetch_related="mentorships")
    mentorship = get_object_or_404(mentor.mentorships.prefetch_related("tasks"), pk=mentorship_pk)
    action = request.GET.get("action")

    context = get_detail_view_context(mentor, mentorship)

    if request.htmx and action == "render_mentorship_info":
        form_html = render_mentorship_info(mentor, mentorship)
        return HttpResponse(form_html)

    context.update(
        paginate_mentorship_request(
            request, mentorship.mentorship_requests.order_by("-date")
        )
    )

    response = TemplateResponse(request, template_name, context)

    return response

@require_http_methods(["GET"])
@login_required
@is_approved
def student_info_view(request, mentorship_request_pk: int):
    """
    Render brief info of a student on a modal
    For detail view
    """
    if not request.htmx:
        return HttpResponseBadRequest('request not made with htmx')

    mentorship_request = get_object_or_404(MentorshipRequest, pk=mentorship_request_pk)
    student = mentorship_request.student

    return TemplateResponse(request, "mentor/student_info_modal.html", {
        "student": student,
        "mentorship_request": mentorship_request,
        "MentorshipRequest": MentorshipRequest,
    })
