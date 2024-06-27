from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.db.models import Q

from django_src.apps.register.models import Student, Mentor
from .models import MentorshipRequest
from .utils import get_mentor, is_approved

@require_GET
@login_required
@is_approved
def list_mentorships(request, username):
    """
    Return a list of mentorships of a mentor

    To be used in the profile view
    """

    template_name = 'mentor/mentor_mentorships.html'
    mentor = get_mentor(username, prefetch_related="mentorships")

    # Mentorships created by mentor
    mentorships = mentor.mentorships.prefetch_related("mentorship_requests")

    # Figure out if the user that is visiting the view is of type mentor or student
    student_queryset = Student.objects.filter(user=request.user)
    is_student = student_queryset.exists()
    is_admin = request.user.is_superuser

    student_requests = None
    not_request_mentorships = mentorships

    # Based on that figure out the action that they can perform based on the state
    if is_student:
        student = student_queryset[0]

        # Get the mentorship requests that belong to the student
        student_requests = MentorshipRequest.objects.filter(student=student, mentorship__mentor=mentor)

        # Get the primary keys of those requests
        student_requests_pks = student_requests.values("pk")

        # Next get the mentorships that the student has not request
        not_request_mentorships = mentorships.filter(~Q(mentorship_requests__pk__in=student_requests_pks))

    # Todo prefetch mentorship requests
    context = {
        "mentor": mentor,
        "mentorships": not_request_mentorships.order_by("name"),
        "is_student": is_student,
        "is_admin": is_admin,
        "student_requests": student_requests,
        "mentorships_empty": not mentorships.exists(),
        "MentorshipRequest": MentorshipRequest,
    }

    response = TemplateResponse(request, template_name, context)
    return response

@require_GET
@login_required
@is_approved
def my_mentorships(request):
    """
    Render the mentorships of the mentor that is logged in
    """

    template_name = 'mentor/my_mentorships.html'
    mentor = get_mentor(request.user.username, prefetch_related="mentorships")


    context = {
        "mentor": mentor,
        "mentorships": mentor.mentorships.order_by("name"),
    }
    context["breadcrumbs"] = [
        {"name": "Mis mentorías"},
    ]

    response = TemplateResponse(request, template_name, context)

    return response


