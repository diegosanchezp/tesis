from django.shortcuts import get_object_or_404
from django_src.apps.auth.views import get_profile_forms
from django_src.apps.register.models import Mentor
from django_src.mentor.utils import loggedin_and_approved
from django.utils.translation import gettext_lazy as _
from django.template.response import TemplateResponse


@loggedin_and_approved
def edit_profile_view(request):
    template_name = "mentor/edit_profile/index.html"
    user = request.user
    mentor = get_object_or_404(Mentor, user=user)

    profile_forms = get_profile_forms(user)

    context = {
        "mentor": mentor,
        **profile_forms,
    }

    return TemplateResponse(request, template=template_name, context=context)
