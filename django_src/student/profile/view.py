from django.template.response import TemplateResponse
from django_src.mentor.utils import loggedin_and_approved
from django.shortcuts import get_object_or_404
from django_src.apps.register.models import Student
from django.views.decorators.http import require_http_methods
from django_src.student.profile.forms import EditStudentForm
from django_src.apps.auth.views import get_profile_forms


def get_GET_context(request):
    user = request.user
    profile_forms = get_profile_forms(user)

    student = get_object_or_404(Student, user=user)
    student_form = EditStudentForm(instance=student)
    student_form.is_valid()

    return {
        "student": student,
        "student_form": student_form,
        **profile_forms,
    }


@require_http_methods(["GET", "POST"])
@loggedin_and_approved
def profile_view(request):
    template_name = "student/profile/index.html"

    context = {}

    if request.method == "GET":
        context.update(get_GET_context(request))

    return TemplateResponse(request, template=template_name, context=context)
