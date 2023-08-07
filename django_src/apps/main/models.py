from django.db import models

from django.utils.translation import gettext_lazy as _

from wagtail.models import (
    Page
)

from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
)
# Create your models here.


class HomePage(Page):
    """
    The HomePage or Promotional page
    """
    template = 'main/home_page.html'

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Logo de la cabecera del home"),
    )

    # --- Hero section header --- #
    header_text = models.CharField(
        max_length=255, help_text=_("Texto introductorio de la página promocional")
    )

    header_cta = models.CharField(
        verbose_name=_("Botón de registrarse"),
        max_length=255,
        help_text=_("Texto del Botón de registrarse"),
    )
    # --- Hero section benefits, four in total --- #

    # First hero section
    hero_one_title = models.CharField(
        max_length=255,
        verbose_name=_("Titulo del primer factor promocional"),
    )

    hero_one_desc = models.TextField(
        verbose_name=_("Descripción del primer factor promocional"),
    )

    hero_one_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Imagen del primer factor promocional"),
    )
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            heading=_("Sección de Cabecera"),
            children=[
                FieldPanel("header_image"),
                FieldPanel("header_text"),
                FieldPanel("header_cta"),
            ],
        ),
        MultiFieldPanel(
            heading=_("Primer Factor promocional"),
            children=[
                FieldPanel("hero_one_title"),
                FieldPanel("hero_one_desc"),
                FieldPanel("hero_one_image"),
            ]
        )
    ]


    # Second
    # hero_two_desc = models.TextField(
    #     verbose_name=_("Descripción segunda sección"),
    # )
    #
    # hero_two_tex = models.CharField(
    #     max_length=255,
    #     help_text=_("Texto de cabecera de la segunda sección"),
    #
    # )
    #
    # hero_two_image = models.ForeignKey(
    #     "wagtailimages.Image",
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL,
    #     related_name="+",
    #     help_text=_(""),
    # )
