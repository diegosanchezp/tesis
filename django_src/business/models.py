from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from wagtail.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    TitleFieldPanel,
    InlinePanel,
)


# ./manage.py dumpdata --natural-primary --indent 4 --verbosity 2 --output /app/fixtures/tmp/jobs.json business.JobOfferIndex business.JobOffer business.JobOfferInterest wagtailcore.Page business.Business


class Business(models.Model):
    user = models.OneToOneField(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="business",
    )

    description = models.TextField(
        verbose_name=_("Descripción"),
    )

    # To have proof of the business existence
    web_page = models.URLField(
        verbose_name=_("Página web"),
    )

    def __str__(self):
        return self.user.get_username()

    class Meta:
        verbose_name = _("Negocio")
        verbose_name_plural = _("Negocios")


class JobOfferIndex(Page):
    """
    A page to list all job offers made by a business
    """

    subpage_types = ["JobOffer"]

    class Meta:
        verbose_name = _("Indice de ofertas de trabajo")
        verbose_name_plural = _("Indices de ofertas de trabajo")


class JobOffer(Page):
    """
    Job offer made by a business
    """

    # To get job offers of a business use: Q(owner__business=)

    class JobType(models.TextChoices):
        IN_PERSON = "IN_PERSON", _("Presencial")
        HIBRID = "HIBRID", _("Híbrido")
        REMOTE = "REMOTE", _("Remoto")

    # Description of the job offer
    description = StreamField(
        verbose_name=_("Descripción del trabajo"),
        block_types=[
            (
                "paragraph",
                blocks.RichTextBlock(
                    features=[
                        "bold",
                        "italic",
                        "ol",
                        "ul",
                        "hr",
                        "link",
                        "superscript",
                        "subscript",
                        "strikethrough",
                        "blockquote",
                        "h2",
                        "h3",
                        "h4",
                    ]
                ),
            ),
        ],
        block_counts={
            "paragraph": {"min_num": 1},
        },
    )

    linkedin_link = models.URLField(
        null=True,
        blank=True,
        verbose_name=_("Link a la oferta en Linkedin"),
        help_text=_(
            "Si esta oferta de trabajo está publicada en Linkedin puedes poner el link aquí"
        ),
    )

    # If job is or remote, not remote, ...
    workplace = models.CharField(
        max_length=255,
        verbose_name=_("Tipo de Lugar de trabajo"),
        choices=JobType.choices,
    )

    content_panels = [
        TitleFieldPanel(
            field_name="title",
            heading=_("Título"),
            help_text=_("Título de la oferta de trabajo"),
            placeholder=_("Título de la oferta de trabajo"),
        ),
        FieldPanel(field_name="workplace"),
        FieldPanel(field_name="linkedin_link"),
        FieldPanel(field_name="description"),
        InlinePanel(relation_name="interests", label=_("Intereses")),
    ]

    # Block the creation of child pages
    subpage_types = []

    # Job offers can be created only under the JobOfferIndex page
    parent_page_types = ["JobOfferIndex"]

    class Meta:
        verbose_name = _("Oferta de trabajo")
        verbose_name_plural = _("Ofertas de trabajo")


class JobOfferInterest(Orderable):
    """|"""

    interest = models.ForeignKey("register.InterestTheme", on_delete=models.CASCADE)

    job_offer = ParentalKey(
        to="JobOffer",
        verbose_name=_("Oferta de trabajo"),
        on_delete=models.CASCADE,
        # Interest themes for the student that is seeking the job
        related_name="interests",
    )

    panels = [
        FieldPanel("interest"),
    ]

    def __str__(self):
        return f"{self.job_offer.title} {self.interest.name}"
