import posixpath
import os

from django.views.generic.base import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.response import TemplateResponse # Delete
from django.views.decorators.http import require_http_methods # Delete
from django import forms

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

@require_http_methods(["GET",])

def forms_demo_view(request):
    from django.forms.renderers import TemplatesSetting


    class FlowbiteFormRenderer(TemplatesSetting):
        form_template_name = "forms/form.html"

    class DemoForm(forms.Form):
        # default_renderer = FlowbiteFormRenderer()
        countries = [("us", "United States"), ("ca", "Canada"), ("mx", "Mexico")]
        email = forms.EmailField(
            label="Your email",
            max_length=100,
            help_text="We'll never share your email with anyone else.",
        )

        country = forms.ChoiceField(
            label="Select your country",
            choices=countries,
        )

        terms_conditions = forms.BooleanField(
            label="I agree to the terms and conditions",
            required=False,
            # help_text="Please read the terms and conditions before proceeding.",
        )

        country_radio = forms.ChoiceField(
            label="Select your country",
            choices=countries,
            widget=forms.RadioSelect(),
        )

        file_inpt = forms.FileField(
            label="Upload file",
            required=False,
            help_text="A profile picture is useful to confirm your are logged into your account",
        )

    form = DemoForm(data={"email": "dwkjaldjaw..ds", "country_radio": "us", "terms_conditions": True, "country": "us"})
    form.is_valid()


    context = {
        "form": form,
    }
    return TemplateResponse(request, "forms/forms_demo.html", context=context)

# Delete later
@require_http_methods(["GET",])
def color_demo_view(request, color: str):

    template_name = "color_demo.html"

    if color == "gris":
        bg_color = "bg-slate-100"
    else:
        bg_color = "bg-[#FFF9DD]"

    return TemplateResponse(request, template_name, {"bg_color": bg_color})
