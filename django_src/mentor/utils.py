import functools
from typing import Any

from django_src.apps.register.models import Mentor, Student, RegisterApprovalStates, RegisterApprovals
from .forms import get_MentorshipTaskFormSet

from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from render_block import render_block_to_string


def is_approved(func):
    """
    Decorator for Checking that a Student or Mentor user is approved
    """

    @functools.wraps(func)
    def inner(request, *args, **kwargs):

        student_queryset = Student.objects.filter(user=request.user)
        mentor_queryset = Mentor.objects.filter(user=request.user)

        is_student = student_queryset.exists()
        is_mentor = mentor_queryset.exists()

        if is_student:
            entity_type = ContentType.objects.get_for_model(Student)
        elif is_mentor:
            entity_type = ContentType.objects.get_for_model(Mentor)
        elif request.user.is_superuser:
            # Admins are always approved
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(_("No tienes permisos para acceder a esta página"))

        approval = RegisterApprovals.objects.filter(user=request.user,user_type=entity_type).last()

        if not approval:
            return HttpResponseForbidden(_("Estas registrado, pero no existe registro de aprobación"))

        if approval.state == RegisterApprovalStates.APPROVED:
            return func(request, *args, **kwargs)
        else:
            return HttpResponseForbidden(_("Tu solicitud de registro no ha sido aprobada"))

    return inner

def loggedin_and_approved(view_func):
    @functools.wraps(view_func)
    def inner(request, *args, **kwargs):
        return login_required(is_approved(view_func))(request, *args, **kwargs)
    return inner

def get_mentor(username: str, prefetch_related: str|None = None):
    """
    Get the mentor by username

    raises 404 if not found
    """

    if prefetch_related:
        queryset = Mentor.objects.prefetch_related(prefetch_related)
    else:
        queryset = Mentor.objects.all()
    mentor = get_object_or_404(queryset, user__username=username)

    return mentor

def validate_add_tasks(request, template_name, block_name: str, context: dict[str, Any], MentorshipTaskFormSet):
    """
    Adds a new empty task field to the mentorship tasks formset
    """

    # create a new formset with the TOTAL_FORMS incremented by 1, this adds
    # a new empty form to the set

    mentorship_tasks_form = MentorshipTaskFormSet(data=request.POST)

    # Trigger validation so errors can be populated
    mentorship_tasks_form.is_valid()

    get_data = request.POST.copy()

    total_forms_key = f"{mentorship_tasks_form.prefix}-TOTAL_FORMS"

    new_extra = int(get_data.get(total_forms_key)) + 1

    get_data[total_forms_key] = str(new_extra)

    mentorship_tasks_form = get_MentorshipTaskFormSet(
        extra=new_extra, max_num=new_extra
    )(data=get_data)

    context.update({
        "mentorship_tasks_form": mentorship_tasks_form
    })

    form_html = render_block_to_string(template_name, block_name, context)
    return HttpResponse(form_html)

def get_page_number(request):
    page_number: str | int | None = request.GET.get("page") or request.POST.get("page")

    if page_number is None:
        page_number = 1
    elif isinstance(page_number, str):
        page_number = int(page_number)

    return page_number
