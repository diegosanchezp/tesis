
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
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


class ProCarreerIndex(Page):
    """
    A page to list and group all the Professional Carreer pages
    """

    page_description = _("Lista de carreras profesional")
    # no app label specified in subpage_types, because BlogPage is in the same app
    # only professional carreers can be added as a subpage
    subpage_types = ['ProfessionalCarreer']

# Create your models here.
class ProfessionalCarreer(Page):
    """
    Professional Carreer model
    """
    template = 'pro_career/pro_carreer.html'
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
        [
            ('paragraph', blocks.RichTextBlock()),
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

