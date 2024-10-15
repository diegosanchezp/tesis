import functools
from django.http.response import HttpResponse, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.template import RequestContext

from render_block import render_block_to_string

from django_src.types import HtmxHttpRequest
from django_src.apps.register.models import Student
from django_src.student.models import StudentJobOffer
from django_src.mentor.utils import loggedin_and_approved
from django_src.utils import get_page_number
from django_src.utils.pagination import page_object_list
from django_src.business.models import JobOffer
from django_src.utils.webui import renderMessagesAsToasts
from .forms import ApplyForm, JobSearchForm, UnApplyForm


jobs_list_template = "student/jobs/jobs_list.html"


@require_http_methods(["GET", "POST"])
@loggedin_and_approved
def jobs_view(request: HtmxHttpRequest):
    """
    List all of the jobs
    """

    # Post request don't need the jobs queryset, that's why is up here
    if request.method == "POST":
        action = request.POST.get("action", None)
        if request.htmx:
            if action == "apply_to_job":
                return apply_to_job(request)
            if action == "unapply_to_job":
                return unapply_to_job(request)


    if request.method == "GET":
        action = request.GET.get("action", None)
        tab = request.GET.get("tab", None)
        jobsearch_form = JobSearchForm(data=request.GET)

        # Get a list of job offers to display
        student = get_student(request)

        context = {
            # Default tab
            "current_tab": "ofertas-trabajo",
            "jobsearch_form": jobsearch_form,
            "search_applied": False,
        }
        jobs_queryset = JobOffer.objects.order_by("-last_published_at")
        # Filter

        if jobsearch_form.is_valid():
            title = jobsearch_form.cleaned_data["title"]
            jobs_queryset = jobs_queryset.filter(title__icontains=title)
            context["search_applied"] = True

        #  If there are multiple StudentJoboffer records related to a single job, each job will appear multiple times in the results, once for each related record.
        # Using a subquery can help avoid duplicates by checking for existence without creating multiple rows:
        subquery = StudentJobOffer.objects.filter(student=student, job=models.OuterRef('pk'))
        jobs_queryset = jobs_queryset.annotate(applied=models.Exists(subquery))

        # Paginate
        per_page = 1
        page_number = get_page_number(request)
        jobs = page_object_list(request, jobs_queryset, per_page=per_page)
        context["jobs"] = jobs


        if isinstance(tab, str) and tab == "ofertas-aplicadas":
            jobs_queryset = jobs_queryset.filter(studentjoboffer__student=student)
            jobs = page_object_list(request, jobs_queryset, per_page=per_page)
            context["current_tab"] = tab
            context["jobs"] = jobs

        if request.htmx and (page_number or action == "render_job_applications"):
            return render_job_applications(request, jobs,context)

        return TemplateResponse(request, jobs_list_template, context)

# def filter_jobsoffers(jobsearch_form: JobSearchForm, jobs_queryset):


def validate_istudent(message: str):
    def decorator_validate_student(view_func):
        @functools.wraps(view_func)
        def wrapper_is_student(request: HtmxHttpRequest, *args, **kwargs):
            if not request.user.is_student:
                response = HttpResponseForbidden(message)
                if request.htmx:
                    messages.success(request, message)
                    renderMessagesAsToasts(request, response)
                return response
            return view_func(request, *args, **kwargs)
        return wrapper_is_student
    return decorator_validate_student


@require_POST
@validate_istudent(_("Solo estudiantes puede des-aplicar a trabajos"))
def unapply_to_job(request: HtmxHttpRequest):
    student = get_student(request)

    # Check that everything is fine
    # Validating the form also ensures thet form.job_application is set
    form = UnApplyForm(student=student, data=request.POST)
    if not form.is_valid():
        response = HttpResponseForbidden()
        if form.errors:
            for error in form.errors:
                messages.error(request, message=error[0])

        renderMessagesAsToasts(request, response)
        return response

    # Delete the the student job offer application
    job_offer: JobOffer = form.cleaned_data["job_offer"]
    job_application = form.job_application
    job_application.delete()

    # Force set applied to false so the card can render correctly
    job_offer.applied = False
    response = render_job_offer_card(request, job_offer)

    messages.success(request, message=_("Desaplicado de la oferta de trabajo"))
    renderMessagesAsToasts(request, response)
    return response


@require_POST
@validate_istudent(_("Solo estudiantes puede aplicar a trabajos"))
def apply_to_job(request):
    student = get_student(request)

    form = ApplyForm(request.POST)

    if form.is_valid():
        job: JobOffer = form.cleaned_data["job"]

        student_job_offer = StudentJobOffer(student=student, job=job)
        student_job_offer.save()

        messages.success(request, _("Aplicado a la oferta de trabajo"))

        # Force set applied to false so the card can render correctly
        job.applied = True
        response = render_job_offer_card(request, job)

        renderMessagesAsToasts(request, response)
        return response

    response = HttpResponseForbidden("something bad happen")
    messages.error(request, message="Error tratanto de aplicar al trabajo")
    renderMessagesAsToasts(request,response)
    return response


def render_job_applications(request, jobs, context):
    template_context = RequestContext(request)
    template_context.update(context)
    template_context.update({
        "jobs": jobs,
    })
    html = render_block_to_string(template_name=jobs_list_template, block_name="job_offer_list", context=context)
    response = HttpResponse(html)
    return response


def render_job_offer_card(request: HtmxHttpRequest, job: JobOffer):
    return TemplateResponse(
        request=request,
        template="student/jobs/job_offer_card.html",
        context={
            "joboffer": job,
        }
    )


def get_student(request: HtmxHttpRequest):
    student: Student = request.user.student
    return student

