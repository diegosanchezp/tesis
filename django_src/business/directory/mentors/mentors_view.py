from django.core.exceptions import PermissionDenied
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_GET
from django.template import RequestContext
from django.db import models
from render_block import render_block_to_string

from django_src.apps.register.models import Mentor
from django_src.utils.pagination import page_object_list
from django_src.mentor.utils import loggedin_and_approved
from .forms import MentorFilterForm, ActionForm, Actions

mentors_directory_template = "business/directory/mentor/mentors.html"

@require_GET
@loggedin_and_approved
def mentors_directory_view(request):

    if not (request.user.is_business or request.user.is_superuser):
        raise PermissionDenied("You are not allowed to view this page")

    per_page = 40

    mentors_queryset = get_mentors_queryset()

    filter_form = MentorFilterForm(data=request.GET)
    action_form = ActionForm(data=request.GET)
    if filter_form.is_valid():
        mentors_queryset = filter_mentors_queryset(mentors_queryset, filters=filter_form.cleaned_data)

    mentors_page = paginate_mentors_queryset(request, mentors_queryset, per_page=per_page)

    context = {
        "Actions": Actions,
        "mentors": mentors_page,
        "filter_form": filter_form,
        "action_form": action_form,
    }

    action_form.is_valid()
    action = None
    if action_form.is_valid():
        action = action_form.cleaned_data["action"]

    if request.htmx:
        # If we are asking to render a new page of we are filtering the mentors
        if request.GET.get("page",None) or action == Actions.FILTER_MENTORS:
            return render_mentor_page(request,context)

    return TemplateResponse(request, mentors_directory_template, context)

def get_mentors_queryset():
    mentors_queryset = Mentor.objects.approved().order_by("-user__first_name")

    return mentors_queryset

def filter_mentors_queryset(mentors_queryset, filters: dict):
    if name_last_name := filters.get("name_last_name"):
        mentors_queryset = mentors_queryset.filter(
            models.Q(user__first_name__icontains=name_last_name)
            | models.Q(user__last_name__icontains=name_last_name)
        )

    if email := filters.get("email"):
        mentors_queryset = mentors_queryset.filter(user__email=email)

    if career := filters.get("career"):
        mentors_queryset = mentors_queryset.filter(carreer=career)

    return mentors_queryset

def paginate_mentors_queryset(request, mentors_queryset, per_page):
    return page_object_list(request, mentors_queryset, per_page=per_page)
    

def render_mentor_page(request, context):

    template_context = RequestContext(request)
    template_context.update(context)

    html = render_block_to_string(template_name=mentors_directory_template, block_name="mentors_list", context=context)
    response = HttpResponse(html)
    return response

