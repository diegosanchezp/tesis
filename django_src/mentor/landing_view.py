from django.db.models.query import QuerySet
from django.http.response import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import models
from django.template.response import TemplateResponse
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from .utils import get_mentor, loggedin_and_approved
from .models import MentorshipRequest
from .forms import MentorshipReqFilterForm

from django_src.settings.wagtail_pages import blogs_index_path
from django_src.apps.register.models import Mentor
from django_src.apps.main.models import EventsIndex, NewsIndex, BlogPage, BlogIndex
from django_src.apps.register.approvals_view import get_page_number
from django_src.apps.main.news_event_views import (
    get_paginated_events,
    get_paginated_news,
    NEWS_SECTION,
    EVENT_SECTION,
)

from render_block import render_block_to_string
from django_htmx.http import trigger_client_event

# Action to filter mentorship requests
FILTER_MENTORSHIP_REQUEST = "filter_mentorship_request"

def filter_mentorship_request(queryset):
    """
    Factory for functions that filter the MentorshipRequest queryset
    """

    # Filter by status
    def by_state(state: MentorshipRequest.State):
        return queryset.filter(status=state)

    # Filter by student name
    def by_student_name(name: str):
        return queryset.filter(
            models.Q(student__user__first_name__icontains=name)
            | models.Q(student__user__last_name__icontains=name)
        )

    return {
        "by_state": by_state,
        "by_student_name": by_student_name,
    }


def get_filter_mentorship_requests(
    mentor: Mentor, student_name: str | None = None, state: str | None = None
) -> QuerySet[MentorshipRequest]:
    """
    Gets the MentorshipRequests queryset of a mentor and filter it by student name or state
    """

    # Get mentorship request queryset
    mentorship_requests = (
        MentorshipRequest.objects.filter(mentorship__mentor=mentor)
        .annotate(
            # Specify the order of the mentorship requests
            order=models.Case(
                models.When(
                    status=MentorshipRequest.State.REQUESTED,
                    then=models.Value(0, output_field=models.IntegerField()),
                ),
                models.When(
                    status=MentorshipRequest.State.CANCELED,
                    then=models.Value(1, output_field=models.IntegerField()),
                ),
                models.When(
                    status=MentorshipRequest.State.REJECTED,
                    then=models.Value(2, output_field=models.IntegerField()),
                ),
                default=models.Value(3, output_field=models.IntegerField()),
            )
        )
        .order_by("order", "date")
    )

    # Setup filters
    filter_fn = filter_mentorship_request(mentorship_requests)
    filter_by_student_name = filter_fn["by_student_name"]
    filter_by_state = filter_fn["by_state"]

    # Filter the queryset if the user has set any filters
    if student_name:
        mentorship_requests = filter_by_student_name(student_name)
    if state:
        mentorship_requests = filter_by_state(state)
    return mentorship_requests


def paginate_mentorship_request(mentorship_requests, page_number: int):
    """
    Paginates the mentorship requests queryset
    """

    # Paginate the queryset
    paginator = Paginator(
        object_list=mentorship_requests, per_page=12
    )  # Change to Show 12 mentorship requests.
    paginated_m_requests = paginator.get_page(page_number)

    return {
        "mentorship_requests": paginated_m_requests,
    }

def render_mentorship_req_table(template_name: str, context: dict):
    """
    Returns an http response with the mentorship request table rendered
    See template mentor/mentorship_req_table.html, for the needed context
    """

    html = render_block_to_string(template_name=template_name, block_name="mentorship_req_table", context=context)
    response = HttpResponse(html)

    return response

def paginate_blogs(blogs_queryset, page_number: int):

    paginator = Paginator(
        object_list=blogs_queryset, per_page=12
    )  # Change to Show 12 mentorship requests.
    blogs_page = paginator.get_page(page_number)
    return blogs_page

@require_http_methods(["GET"])
@loggedin_and_approved
def landing_view(request):
    """
    Main dashboard for the currently logged in user
    """
    if not (request.user.is_mentor or request.user.is_superuser):
        raise PermissionDenied

    template = "mentor/landing.html"
    mentor = get_mentor(request.user.get_username())
    events_index = EventsIndex.objects.first()
    news_index = NewsIndex.objects.first()
    page_number = get_page_number(request)
    blogs_index = BlogIndex.objects.get(path=blogs_index_path)
    myblogs_queryset = BlogPage.objects.filter(owner=mentor.user).order_by("-last_published_at")
    myblogs_paginated = paginate_blogs(myblogs_queryset, page_number=1)

    filter_form = MentorshipReqFilterForm(data=request.GET)
    filter_form.is_valid()
    student_name = filter_form.cleaned_data["student_name"]
    state = filter_form.cleaned_data["state"]

    mentorship_requests = get_filter_mentorship_requests(mentor, student_name, state)

    context = {
        "mentor": mentor,
        "myblogs": myblogs_paginated,
        "blogs_count": myblogs_paginated.object_list.count(),
        # The url to add a blog, redirects to the wagtail cms
        "add_blog_url": reverse(
            "wagtailadmin_pages:add_subpage", kwargs={"parent_page_id": blogs_index.id}
        ),
        "filter_form": filter_form,
        "EVENT_SECTION": EVENT_SECTION,
        "NEWS_SECTION": NEWS_SECTION,
        "events_index": events_index,
        "news_index": news_index,
        **get_paginated_news(
            page_obj_name="news",
            page_number_name="news_page_number",
            paginator_name="news_paginator",
        ),
        **get_paginated_events(
            page_obj_name="events",
            page_number_name="events_page_number",
            paginator_name="events_paginator",
        ),
        **paginate_mentorship_request(mentorship_requests, page_number),
    }

    if request.htmx:
        action = request.GET.get("action")
        if action == FILTER_MENTORSHIP_REQUEST:
            return render_mentorship_req_table(template, context)
        else:
            HttpResponseForbidden("Invalid action")


    return TemplateResponse(request, template, context)
