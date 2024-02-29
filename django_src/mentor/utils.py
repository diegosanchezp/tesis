from django_src.apps.register.models import Mentor

from django.shortcuts import get_object_or_404

def get_mentor(username: str, prefetch_related: str):
    """
    Get the mentor by username

    raises 404 if not found
    """

    return get_object_or_404(Mentor.objects.prefetch_related(prefetch_related), user__username=username)

