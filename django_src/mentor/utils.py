from django_src.apps.register.models import Mentor, Student, RegisterApprovalStates, RegisterApprovals

from django_src.apps.auth.models import User
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

import functools

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

