from django.db import models
from django.http.response import HttpResponseBadRequest
from django.urls.base import reverse_lazy


from django.utils.translation import gettext_lazy as _
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator, MaxValueValidator
)

from wagtail.models import (
    Page,
)

from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.images.blocks import ImageChooserBlock

from wagtail.admin.panels import (
    FieldPanel,
)
from django_src.apps.register.models import Mentor

EXP_TAB = "experiencias"
class ProCarreerIndex(Page):
    """
    A page to list and group all the Professional Carreer pages
    """

    page_description = _("Lista de carreras profesional")
    # no app label specified in subpage_types, because ProfessionalCarreer is in the same app
    # only professional carreers can be added as a subpage
    subpage_types = ['ProfessionalCarreer']

# Create your models here.
class ProfessionalCarreer(Page):
    """
    Professional Carreer model
    """
    template = 'pro_carreer/pro_carreer.html'
    page_description = _("Carrera profesional")


    # --- DB columns definition ---
    short_description = models.CharField(
        verbose_name=_("Descripción corta"),
        max_length=250,
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen para la descripción corta"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Imagen del factor promocional"),
    )

    content = StreamField(
        verbose_name=_("Contenido"),
        block_types=[
            ('paragraph', blocks.RichTextBlock(features=["bold", "italic", "ol", "ul", "hr", "link", "document-link", "code", "superscript", "subscript", "strikethrough", "blockquote", "h2", "h3", "h4"])),
            ('image', ImageChooserBlock()),
        ],
        block_counts={
            'paragraph': {'min_num': 1},
        },
        use_json_field=True
    )
    # --- DB End columns definition ---

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel("image"),
        FieldPanel("short_description"),
        FieldPanel("content"),
    ]

    # Todo: this page can only be the created by the root page
    parent_page_types = ["ProCarreerIndex"]
    # Block the creation of child pages
    subpage_types = []

    @property
    def add_query_string(self):
        """
        To be used in templated for a mentor to add an experience
        """
        return f"?tab={EXP_TAB}"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["mentors"] = Mentor.objects.filter(my_career_experiences__pro_carreer=self)
        context["breadcrumbs"] = [
            {"name": "Carreras profesionales", "href": reverse_lazy("pro_carreer:student_carreer_match")},
            {"name": self.title },
        ]
        return context

    def serve(self, request):
        # Putting this import here to avoid circular imports exception
        # Because experience_view does use the models defined in this file
        from . import experience_view

        response = super().serve(request)

        if request.method == "POST":
            if "action" in request.POST:
                if request.htmx:
                    action = request.POST["action"]
                    if action == "edit_exp":
                        return experience_view.edit_exp(
                            request, pk_pro_career_exp=int(request.POST["pk"])
                        )
                    elif action == "add_exp":
                        return experience_view.add_exp(
                            request, pro_carreer=self,
                        )

                    elif action == "delete_exp":
                        return experience_view.delete_exp(
                            request, pk_pro_career_exp=int(request.POST["pk"])
                        )
                    else:
                        return HttpResponseBadRequest(content="Invalid action")

        if request.method == "GET":
            tab_name = "experiencias"

            if "tab" in request.GET:
                if request.GET["tab"] == tab_name:
                    if "action" in request.GET:
                        if request.htmx:
                            action = request.GET["action"]
                            if  action == "render_exp_form":
                                return experience_view.render_exp_form(
                                    request=request,
                                    pk_pro_career_exp=int(request.GET["pk"]),
                                )

                            if action == "render_empty_exp_form":
                                return experience_view.render_empty_exp_form(request)
                            if action == "render_distribution":
                                return experience_view.render_distribution(request, pro_career=self)


                    return experience_view.view(request, page=self)
        return response

def get_rating_range_selected(rating: int):
    """
    Get a range object for the selected stars
    """

    return range(1, rating + 1)

def get_rating_range_unselected(rating: int):
    """
    Get a range object for the unfilled stars
    """

    return range(rating+1, 5+1)

class ProCarreerExperience(models.Model):
    """
    Opinionated experience of a career by a mentor
    """

    pro_carreer = models.ForeignKey(
        to="ProfessionalCarreer",
        verbose_name=_("Carrera profesional"),
        on_delete=models.CASCADE,
        related_name="career_experiences",
    )

    mentor = models.ForeignKey(
        to="register.Mentor",
        verbose_name=_("Mentor"),
        on_delete=models.CASCADE,
        related_name="my_career_experiences",
    )

    experience = models.TextField(
        verbose_name=_("Experiencia"),
        validators=[MinLengthValidator(4)],
        null=False,
        blank=False,
    )

    rating = models.PositiveIntegerField(
        verbose_name=_("Calificación"),
        # validate between 1 and 5
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=False,
        blank=False,
    )

    init_year=models.DateField(
        verbose_name=_("Año inicio"),
    )

    end_year=models.DateField(
        verbose_name=_("Año fin"),
        null=True,
        blank=True,
    )

    company = models.CharField(
        verbose_name=_("Empresa"),
        validators=[MinLengthValidator(1)],
    )

    class Meta:
        unique_together = [["pro_carreer", "mentor"]]

    def __str__(self) -> str:
        return f"{self.mentor} {self.rating}"

    @property
    def rating_range_selected(self):
        """
        Get a range object for the selected stars

        Use in django templates
        """
        return get_rating_range_selected(self.rating)

    @property
    def rating_range_unselected(self):
        """
        Get a range object for the unfilled stars

        Use in django templates
        """
        return get_rating_range_unselected(self.rating)

    @property
    def edit_querystring(self):
        return f"?tab={EXP_TAB}&pk={self.pk}"
