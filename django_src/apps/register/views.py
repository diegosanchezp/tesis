from urllib.parse import urlencode
from collections import OrderedDict

from django.db.models import Prefetch, Q, Value, Case, When
from django.db import models

from django.views.generic import ListView, CreateView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.template.response import TemplateResponse

from django.http import HttpResponse, QueryDict
from django.urls import reverse_lazy

from .models import Faculty, Carreer

# Create your views here.
class MainView(TemplateView):
    template_name = "register/main.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        select_carrera_url = reverse_lazy("register:select_carrera")
        context["form_urls"] = {
            "estudiante": select_carrera_url,
            "mentor": select_carrera_url,
            "empresa": "todo",
        }
        return context

# common steps between the mentor and student
step_urls = {
    "select_perfil": reverse_lazy("register:index"), #1
    "select_carrera": reverse_lazy("register:select_carrera"), #2
}

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
        context["step_urls"] = step_urls
        return context

class SelectCarrerSpecialization(DetailView):
    template_name = "register/carrer_specialization.html"
    model = Carreer
    context_object_name = "carreer"
    slug_field = "name"
    slug_url_kwarg = "name"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["step_urls"] = step_urls
        carreer: Carreer = context[self.context_object_name]
        context["specializations_json"] = list(
            carreer.carrerspecialization_set.all().values("name")
        )
        context["urlCarrer"] = self.kwargs[self.slug_url_kwarg]
        return context

    def get_queryset(self):
        carrer_set = super().get_queryset()
        # prefetch all specialization to avoid performance problems
        carrer_set.prefetch_related("carrerspecialization_set")
        return carrer_set

class SelecThemeView(SingleObjectMixin, ListView):

    template_name = "register/select_theme.html"
    paginate_by = 4

    slug_field = "name"
    slug_url_kwarg = "name"
    # context_object_name="interest_themes"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Carreer.objects.all())

        # Themes from url
        self.selected_themes_list = self.request.GET.getlist("theme")

        super_response = super().get(request, *args, **kwargs)
        if not request.htmx:
            return super_response

        # 3. Student has selected one or more themes and it's requesting a new page of themes

        # Get context data for render_block_to_string
        ctx = self.get_context_data()
        ullist_html = render_block_to_string(self.template_name, "theme_list", ctx)

        # Make a response with the rendered new list of themes
        htmx_reponse = HttpResponse(ullist_html)

        return htmx_reponse


    def get_queryset(self):
        interest_themes = self.object.interest_themes

        # 1. Student hasn't selected any theme
        if len(self.selected_themes_list) == 0:

            # Order by is need to yield consistent pagination results
            return interest_themes.order_by("name")


        # 2. Student has selected one or more themes

        selected_themes_query = Q(name__in=self.selected_themes_list)

        selected_themes = interest_themes.filter(selected_themes_query).annotate(
            # Add metadata column to know that the value is selected
            selected=Value(True, output_field=models.BooleanField()),
            # Add metadata column to keep the original order
            relevancy=Case(
                # Make the order
                *[
                    When(name=theme, then=Value(idx, output_field=models.IntegerField()))
                    for idx,theme in enumerate(self.selected_themes_list)
                ],
            ),
        )

        rest_of_themes = interest_themes.filter(~selected_themes_query).annotate(
            # Add metadata column to know that the value is not selected
            selected=Value(False, output_field=models.BooleanField()),
            # Add metadata column to keep the original order
            relevancy=Value(len(self.selected_themes_list) + 1, output_field=models.IntegerField())
        )

        # Make union of querysets and order the resulting set so that the selected themes
        # are showed first
        all_themes = selected_themes.union(rest_of_themes).order_by(
            "-selected",
            "relevancy",
            # Id makes the sort unique, otherwise, repeated elements might appear in the pages.
            # https://stackoverflow.com/questions/5044464/django-pagination-is-repeating-results
            "id"
        )

        return all_themes


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["carreer"] = self.object
        context["urlCarrer"] = self.kwargs[self.slug_url_kwarg]
        context["url_themes"] = self.selected_themes_list

        # Encode the selected themes as query parameter
        themes_query_str = QueryDict(mutable=True)
        themes_query_str.setlist("theme", self.selected_themes_list)
        context["themes_query_param"] = themes_query_str.urlencode()
        context["themes_query_param_len"] = len(self.selected_themes_list)

        # Add urls for previous steps
        context["step_urls"] = {
            **step_urls,
            "specialization": reverse_lazy(
                "register:select_specialization",
                kwargs={
                    self.slug_url_kwarg: self.kwargs[self.slug_url_kwarg]
                }
            )
        }

        return context

def register_sucess_view(request):
    return TemplateResponse(request, 'register/success.html', {})

