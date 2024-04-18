from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required

from .utils import get_mentor

from django.template.response import TemplateResponse

from django_src.apps.main.models import BlogPage

@require_GET
@login_required
def view(request, username):
    template_name = "mentor/blogs.html"

    mentor = get_mentor(username, prefetch_related="user__owned_pages")

    blogs = BlogPage.objects.filter(owner=mentor.user).order_by("-last_published_at")

    context = {
        "mentor": mentor,
        # order blogs by last_published_at descending
        "blogs": blogs,
    }
    return TemplateResponse(request, template_name, context)