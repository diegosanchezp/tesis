from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from .utils import get_mentor

@require_GET
@login_required
def view(request, username):
    """
    Main view of a mentor profile
    """

    template_name = 'mentor/profile.html'
    mentor = get_mentor(username, prefetch_related="experiences")

    # Order mentor experiences by init_year descending
    experiences = mentor.experiences.all().order_by("-init_year")

    # select related experiences
    context = {
        "mentor": mentor,
        "experiences": experiences,
    }

    response = TemplateResponse(request, template_name, context)
    return response
