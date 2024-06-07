from django_src.business.models import JobOffer, JobOfferIndex
from django.template.response import TemplateResponse
from django_src.mentor.utils import loggedin_and_approved
from django.core.paginator import Paginator
from django_src.settings.wagtail_pages import jobs_index_path
from django.urls import reverse
from django.core.exceptions import PermissionDenied


def get_job_offers_queryset(user):
    return JobOffer.objects.filter(owner=user)


def paginate_job_offers(job_offers, page_number: int):

    # Paginate the queryset
    paginator = Paginator(
        object_list=job_offers, per_page=10
    )  # Change to Show 10 mentorship requests.

    return paginator.get_page(page_number)


@loggedin_and_approved
def landing_view(request):

    if not (request.user.is_business or request.user.is_superuser):
        raise PermissionDenied

    template_name = "business/landing/landing.html"
    job_offers_queryset = get_job_offers_queryset(user=request.user)
    job_offers_page = paginate_job_offers(job_offers_queryset, page_number=1)
    job_index = JobOfferIndex.objects.get(path=jobs_index_path)

    context = {
        "job_offers": job_offers_page,
        # The url to add a new job offer, redirects to the wagtail cms
        "add_url": reverse(
            "wagtailadmin_pages:add_subpage", kwargs={"parent_page_id": job_index.id}
        ),
    }

    return TemplateResponse(request, template=template_name, context=context)
