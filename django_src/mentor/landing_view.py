from django.http.response import HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import models
from django.template.response import TemplateResponse

from django_src.apps.register.models import Mentor

from .utils import get_mentor, loggedin_and_approved
from .models import MentorshipRequest
from .forms import MentorshipReqFilterForm

from django_src.apps.main.models import EventsIndex, NewsIndex
from django_src.apps.register.approvals_view import get_page_number
from django_src.apps.main.news_event_views import (
    get_paginated_events,
    get_paginated_news,
    NEWS_SECTION,
    EVENT_SECTION,
)

from render_block import render_block_to_string
from django_htmx.http import trigger_client_event

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
):
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
        object_list=mentorship_requests, per_page=1
    )  # Change to Show 10 mentorship requests.
    paginated_m_requests = paginator.get_page(page_number)

    return {
        "mentorship_requests": paginated_m_requests,
    }


@require_http_methods(["GET"])
@loggedin_and_approved
def landing_view(request):
    template = "mentor/landing.html"
    mentor = get_mentor(request.user.get_username())
    events_index = EventsIndex.objects.first()
    news_index = NewsIndex.objects.first()
    page_number = get_page_number(request)

    filter_form = MentorshipReqFilterForm(data=request.GET)
    filter_form.is_valid()
    student_name = filter_form.cleaned_data["student_name"]
    state = filter_form.cleaned_data["state"]

    mentorship_requests = get_filter_mentorship_requests(mentor, student_name, state)

    context = {
        "mentor": mentor,
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
        if action == "filter_mentorship_request":
            html = render_block_to_string(template_name=template, block_name="mentorship_req_table", context=context)
            response = HttpResponse(html)
            # Tell the client to re-attach htmx pagination handler
            trigger_client_event(
                response=response,
                name="reAttachPagination",
                after="swap", # very important
            )
            return response
        else:
            HttpResponseForbidden("Invalid action")


    return TemplateResponse(request, template, context)
