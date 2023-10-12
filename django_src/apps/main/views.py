import posixpath
import os

from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

# Create your views here.

class PrivateMediaView(LoginRequiredMixin, View):
    """
    Check access to private media files
    """

    def get(self, request, file_path: str):
        # Remove trailing slash
        path = posixpath.normpath(file_path).lstrip("/")

        # Make a response with appropriate headers
        response = HttpResponse(headers={
            # Redirect to nginx internal endpoint 
            "X-Accel-Redirect": f"/pmedia/{path}",
            # Reset Content-Type otherwise is incorrectly set
            "Content-Type": "",
        });

        # Tell NGNIX everything the request is authenticated
        return response


class ComponentsDemoView(TemplateView):
    """
    Components demo view
    """

    def get(self, request, *args, **kwargs):
        # Parametrized template name
        self.template_name = f"components/demos/{kwargs.get('template_name')}.html"
        return super().get(request,*args,**kwargs)
