from django.views.generic.base import TemplateView
from django.urls import reverse

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
    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context["step_urls"] = {
            "select_perfil": reverse("register:index")
        }
        return context
