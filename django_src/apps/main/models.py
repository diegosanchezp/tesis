from django.db import models

from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey

from wagtail.models import (
    Page,
    Orderable
)

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
)
from wagtail.fields import RichTextField
# Create your models here.
class HeroSection(Orderable):
    page = ParentalKey(
        "HomePage",
        on_delete=models.CASCADE,
        related_name='hero_sections',
        verbose_name="",
    )

    title = models.CharField(
        max_length=255,
        verbose_name=_("Titulo del factor promocional"),
    )

    description = models.TextField(
        verbose_name=_("Descripción del factor promocional"),
    )

    image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Imagen del factor promocional"),
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('title'),
        FieldPanel('description'),
    ]

class HomePage(Page):
    """
    The HomePage or Promotional page
    """
    template = 'main/home_page.html'

    page_description = _("Esta es la página principal de este sitio.")

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen cabecera"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Logo de la cabecera del home"),
    )

    # --- Hero section header --- #
    header_text = models.CharField(
        max_length=255,
        verbose_name=_("Texto introductorio de la página promocional")
    )

    header_cta = models.CharField(
        verbose_name=_("Botón de registrarse"),
        max_length=255,
        help_text=_("Texto del Botón de registrarse"),
    )
    # --- Hero section benefits, four in total --- #

    # First hero section
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading=_("Sección de Cabecera"),
            children=[
                FieldPanel("header_image"),
                FieldPanel("header_text"),
                FieldPanel("header_cta"),
            ],
        ),
        InlinePanel(
            relation_name='hero_sections',
            label=_("Factor promocional"),
            min_num=2,
            heading=_("Factores promocionales")
        ),
    ]

    # Block the creation of child pages
    subpage_types = ['BlogIndex', 'pro_carreer.ProCarreerIndex', ]

class BlogIndex(Page):
    """
    A page to list all the BlogPages
    """

    # no label specified in subpage_types, because BlogPage is in the same app
    subpage_types = ['BlogPage']

class BlogPage(Page):
    template = "main/blog.html" # Todo
    page_description = _("Blog")

    # Optional image
    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen del blog"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Thumbnail del blog"),
    )

    # When set to True, the Wagtail editor will not allow any users to edit the content of the page,
    # only the owner
    locked = True

    content = RichTextField(
        verbose_name=_("Contenido del blog")
    )

    content_panels = Page.content_panels + [
        FieldPanel("thumbnail"),
        FieldPanel("content")
    ]

    # Block the creation of child pages
    subpage_types = []
