from django.template.response import TemplateResponse
from django.core.paginator import Paginator
from django_src.settings.wagtail_pages import jobs_index_path
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http.response import HttpResponse, HttpResponseNotFound

from render_block import render_block_to_string

from django_src.utils.webui import renderMessagesAsToasts
from django_src.business.models import JobOffer, JobOfferIndex
from django_src.student.models import StudentJobOffer
from django_src.mentor.utils import loggedin_and_approved
from django_src.apps.main.news_event_views import (
    get_paginated_events,
    get_paginated_news,
    NEWS_SECTION,
    EVENT_SECTION,
    get_news_evt_index,
)
from django_src.business.landing.forms import GetJobApplicationForm


def get_job_offers_queryset(user):
    return JobOffer.objects.filter(owner=user)

def get_applications_queryset(user):
    # order by application date
    return StudentJobOffer.objects.filter(job__owner=user).order_by("-date")

def paginate_job_offers(job_offers, page_number: int):

    # Paginate the queryset
    paginator = Paginator(
        object_list=job_offers, per_page=10
    )  # Change to Show 10 job offers.

    return paginator.get_page(page_number)

def paginate_job_applications(applications, page_number: int):

    # Paginate the queryset
    paginator = Paginator(
        object_list=applications, per_page=10
    )  # Change to Show 10 mentorship requests.

    return paginator.get_page(page_number)

def get_job_application_modal(request, student_id, job_id):
    
    template_name = "business/landing/job_offer_modal.html"

    context = {
        "job_application": get_object_or_404(StudentJobOffer, student=student_id, job=job_id),
    }

    return TemplateResponse(request, template=template_name, context=context)

def render_job_applications_table(job_applications):
    context = {
        "job_applications": job_applications
    }
    html = render_block_to_string(template_name="business/landing/landing.html", block_name="job_applications_table", context=context)
    response = HttpResponse(html)

    return response


@loggedin_and_approved
def landing_view(request):

    if not (request.user.is_business or request.user.is_superuser):
        raise PermissionDenied

    template_name = "business/landing/landing.html"
    job_offers_queryset = get_job_offers_queryset(user=request.user)
    job_offers_page = paginate_job_offers(job_offers_queryset, page_number=1)
    job_index = JobOfferIndex.objects.get(path=jobs_index_path)
    job_applications = paginate_job_applications(
        get_applications_queryset(request.user),
        page_number=request.GET.get("page", 1),
    )

    context = {
        "job_offers": job_offers_page,
        "job_applications": job_applications,
        "job_offer_count": job_offers_page.object_list.count(),
        # The url to add a new job offer, redirects to the wagtail cms
        "add_url": reverse(
            "wagtailadmin_pages:add_subpage", kwargs={"parent_page_id": job_index.id}
        ),
        # News and events
        "EVENT_SECTION": EVENT_SECTION,
        "NEWS_SECTION": NEWS_SECTION,
        **get_news_evt_index(),
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
    }

    if request.method == "GET":
        action = request.GET.get("action", None)
        if action == "get_job_application_modal":
            form = GetJobApplicationForm(data=request.GET)
            if form.is_valid():
                job_id = form.cleaned_data["job"].pk
                student_id = form.cleaned_data["student"].pk
                return get_job_application_modal(request, student_id, job_id)
            else:
                # TODO TEST: message 404 student job offer not found
                response = HttpResponseNotFound()

                messages.error(request, _("No existe estudiante que haya aplicado a esta oferta de trabajo"))
                renderMessagesAsToasts(request, response)
                return response

        if action == "render_job_applications_table":
            return render_job_applications_table(job_applications)

    return TemplateResponse(request, template=template_name, context=context)
