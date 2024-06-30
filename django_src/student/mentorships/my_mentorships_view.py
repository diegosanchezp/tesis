from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.db import models
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from render_block.base import render_block_to_string

from django_src.apps.register.models import Student
from django_src.mentor.models import MentorshipHistory, MentorshipRequest, StudentMentorshipTask
from django.views.decorators.http import require_http_methods

my_mentorships_template = "student/my_mentorships.html"

def get_student_mentorships(student):

    students_info = MentorshipHistory.objects.annotate(
        task_todo=models.Count(
            "mentorship__tasks__student_tasks",
            filter=models.Q(
                mentorship__tasks__student_tasks__state=StudentMentorshipTask.State.TODO,
                mentorship__tasks__student_tasks__student=student,
            ),
            distinct=True
        ),
        tasks_in_progress=models.Count(
            "mentorship__tasks__student_tasks",
            filter=models.Q(
                mentorship__tasks__student_tasks__state=StudentMentorshipTask.State.IN_PROGRESS,
                mentorship__tasks__student_tasks__student=student,
            ),
            distinct=True
        ),
        tasks_completed=models.Count(
            "mentorship__tasks__student_tasks",
            filter=models.Q(
                mentorship__tasks__student_tasks__state=StudentMentorshipTask.State.COMPLETED,
                mentorship__tasks__student_tasks__student=student,
            ),
            distinct=True
        ),
        task_total=models.Count("mentorship__tasks", distinct=True),
        is_completed=models.Case(
            models.When(tasks_completed=models.F("task_total"), then=True),
            default=False,
            output_field=models.BooleanField()
        ),
    )
    return students_info

def get_mentorship_requests(student):
    mentorships_requests = MentorshipRequest.objects.filter(
        models.Q(student=student),
        models.Q(status=MentorshipRequest.State.REQUESTED) | Q(status=MentorshipRequest.State.REJECTED)
    )
    return mentorships_requests

@require_http_methods(["GET"])
def render_request_list(request, mentorships_requests):
    html =  render_block_to_string(
        template_name=my_mentorships_template,
        block_name="mentorships_requests_list",
        context={
            "mentorships_requests": mentorships_requests,
        }
    )
    return HttpResponse(html)


@require_http_methods(["GET"])
def student_mentorships_view(request):
    template_name = my_mentorships_template

    student = get_object_or_404(Student, user=request.user)

    mentorship_query = get_student_mentorships(student)
    mentorships_in_progress = mentorship_query.filter(
        student=student,
        state=MentorshipHistory.State.ACCEPTED,
    )
    mentorships_requests = get_mentorship_requests(student)

    context = {
        "mentorships_in_progress": mentorships_in_progress,
        "mentorships_requests": mentorships_requests,
        "MentorshipRequest": MentorshipRequest,
        "student": student,
    }

    context["breadcrumbs"] = [
        {"name": "Mis mentorías"},
    ]

    action = request.GET.get("action")
    if action == "render_request_list":
        return render_request_list(request, mentorships_requests)

    return TemplateResponse(request, template=template_name, context=context)
