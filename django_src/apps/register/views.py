from django.db.models.aggregates import Count
from django.db.models.expressions import When
from django.views.generic.base import TemplateView
from django.http import HttpResponse
from django.db.models import Prefetch, Q
from django.urls import reverse
from .models import Faculty, Carreer
from render_block import render_block_to_string

# Create your views here.
class MainView(TemplateView):
    template_name = "register/main.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        select_carrera_url = reverse("register:select_carrera")
        context["form_urls"] = {
            "estudiante": select_carrera_url,
            "mentor": select_carrera_url,
            "empresa": "todo",
        }
        return context

class SelectCarreraView(TemplateView):
    template_name = "register/select_carrera.html"

    def get(self, request, *args, **kwargs):
        # Super also calls get_context_data
        super_response = super().get(request, *args, **kwargs)

        # Handle htmx request
        if request.htmx:
            # Get context data for render_block_to_string
            ctx = self.get_context_data()
            form_html = render_block_to_string(self.template_name, "carrer_form", ctx)
            # Make a response with the rendered html block
            return HttpResponse(form_html)

        # Return normal reponse
        return super_response

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        facultys = Faculty.objects.prefetch_related("carreers")

        if self.request.htmx:
            search_key = self.request.GET["search"]
            if search_key != "":

                # First get the carrers that matches the search key
                carreers = Carreer.objects.filter(name__icontains=search_key)

                # Then get the facultys of the carrers that matches
                facultys = Faculty.objects.filter(
                    pk__in=carreers.values("faculty_id")
                ).prefetch_related(
                    Prefetch(
                        "carreers",
                        # Instead of listing all the carreers, force to list those carreers
                        # that matches the search_key
                        queryset=carreers
                    )
                )

        # The facultys and carreers to render on a grid
        context["facultys"] = facultys

        # faculty_num is used to determine the number of columns of the grid of facultys
        context["faculty_num"] = facultys.count()
        context["step_urls"] = {
            "select_perfil": reverse("register:index")
        }
        return context
