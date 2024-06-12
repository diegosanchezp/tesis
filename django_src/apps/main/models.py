from django.db import models
from django.http.response import HttpResponse
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import truncatechars
from render_block import render_block_to_string
from modelcluster.fields import ParentalKey
from django_src.customwagtail.permission_tester import MyPagePermissionTester
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, Orderable
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    InlinePanel,
    FieldRowPanel,
)

from django_src.apps.register.approvals_view import get_page_number
from django_src.utils import remove_index_publish_permission

MAX_TITLE_LENGHT = 100


# Create your models here.
class HeroSection(Orderable):
    page = ParentalKey(
        "HomePage",
        on_delete=models.CASCADE,
        related_name="hero_sections",
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
        FieldPanel("image"),
        FieldPanel("title"),
        FieldPanel("description"),
    ]


class HomePage(Page):
    """
    The HomePage or Promotional page
    """

    template = "main/home_page.html"

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
        max_length=255, verbose_name=_("Texto introductorio de la página promocional")
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
            relation_name="hero_sections",
            label=_("Factor promocional"),
            min_num=2,
            heading=_("Factores promocionales"),
        ),
    ]

    # Only allow this child pages
    subpage_types = [
        "BlogIndex",
        "pro_carreer.ProCarreerIndex",
        "NewsIndex",
        "business.JobOfferIndex",
    ]


class BlogIndex(Page):
    """
    A page to list all the BlogPages
    """

    # no label specified in subpage_types, because BlogPage is in the same app
    subpage_types = ["BlogPage"]

    def permissions_for_user(self, user):
        """
        Override this method to remove the publish permission from certain users
        on this blog index page
        """

        page_permission_tester = super().permissions_for_user(user)
        return remove_index_publish_permission(page_permission_tester, user)


class BlogPage(Page):
    """
    A Mentor's Blog
    """

    template = "main/blog.html"
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

    content = StreamField(
        verbose_name=_("Contenido del blog"),
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
                        "document-link",
                        "code",
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
            ("image", ImageChooserBlock()),
        ],
        block_counts={
            "paragraph": {"min_num": 1},
        },
        use_json_field=True,
    )

    content_panels = Page.content_panels + [
        FieldPanel("thumbnail"),
        FieldPanel("content"),
    ]

    # Block the creation of child pages
    subpage_types = []

    def permissions_for_user(self, user):
        """
        Mentors can unpublish, but not, publish their blogs
        """
        # Override the method to use the custom permission tester
        page_permission_tester = MyPagePermissionTester(user, self)
        return page_permission_tester


class NewsIndex(Page):
    """
    Acts like a folder list all Pages of type News
    """

    template = "main/news/news_index.html"

    # Only allow NewsPage as child pages
    subpage_types = ["NewsPage"]

    def __init__(self, *args, **kwargs):
        # importing here to avoid circular imports, because get_wagtailpage_paginated uses the models defined on this file
        from django_src.apps.main.news_event_views import get_wagtailpage_paginated

        super().__init__(*args, **kwargs)
        self.get_paginated_events = get_wagtailpage_paginated(
            PageModel=NewsPage,
            per_page=20,
        )

    def serve(self, request):
        # Add suppor for pagination to this index page
        response = super().serve(request)
        if request.htmx and request.GET:
            context = self.get_context(request)
            html = render_block_to_string(
                block_name="news_cards",
                template_name=self.template,
                context=context,
            )
            return HttpResponse(html)

        return response

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        page_number = get_page_number(request)

        # Add extra variables and return the updated context
        news = NewsPage.objects.child_of(self).live().order_by("-last_published_at")
        context["breadcrumbs"] = [
            {"name": "Noticias"},
        ]
        context.update(
            self.get_paginated_events(
                page_obj_name="news", page_number=page_number, queryset=news
            )
        )
        return context


class NewsPage(Page):
    """
    News that will appear to Admins
    """

    template = "main/news/news.html"

    page_description = _("Noticia")

    description = models.CharField(
        max_length=255,
        verbose_name=_("Descripción breve"),
        help_text=_("Escribe una descripción corta de sobre la noticia"),
    )

    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen de la noticia"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Imagen pequeña (thumbnail) de la noticia"),
    )

    content = StreamField(
        verbose_name=_("Contenido de la noticia"),
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
                        "document-link",
                        "code",
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
            ("image", ImageChooserBlock()),
        ],
        block_counts={
            "paragraph": {"min_num": 1},
        },
    )

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel(field_name="thumbnail"),
        FieldPanel(field_name="description"),
        FieldPanel(field_name="content"),
    ]

    # News pages can be created only under the NewsIndex page
    parent_page_types = ["NewsIndex"]

    # Block the creation of child pages
    subpage_types = []

    class Meta:
        # https://docs.wagtail.org/en/stable/topics/pages.html#friendly-model-names
        verbose_name = _("Noticia")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        parent = self.get_parent()
        context["breadcrumbs"] = [
            {"name": "Noticias", "href": parent.get_url(request=request)},
            {"name": truncatechars(self.title, MAX_TITLE_LENGHT)},
        ]
        return context


class EventPage(Page):
    """
    News that will appear to Admins
    """

    template = "main/event_page.html"

    page_description = _("Evento")

    description = models.CharField(
        max_length=255,
        verbose_name=_("Descripción breve"),
        help_text=_("Descripción corta de sobre el evento"),
    )

    start_date = models.DateTimeField(
        verbose_name=_("Fecha de inicio"),
    )

    end_date = models.DateField(
        verbose_name=_("Fecha de finalización"),
        null=True,
        blank=True,
    )
    # where the event takes place
    place = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Lugar del evento"),
        help_text=_("El lugar donde se llevará a cabo el evento"),
    )

    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        verbose_name=_("Imagen principal del evento"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text=_("Imagen pequeña (thumbnail) del evento"),
    )

    content = StreamField(
        verbose_name=_("Contenido del evento"),
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
                        "document-link",
                        "code",
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
            ("image", ImageChooserBlock()),
        ],
        block_counts={
            "paragraph": {"min_num": 1},
        },
    )

    # Editor panels configuration
    content_panels = Page.content_panels + [
        FieldPanel(field_name="thumbnail"),
        FieldRowPanel(
            heading=_("Fechas"),
            children=[
                FieldPanel(field_name="start_date"),
                FieldPanel(field_name="end_date"),
            ],
        ),
        FieldPanel(field_name="description"),
        FieldPanel(field_name="content"),
    ]

    # News pages can be created only under the EventsIndex page
    parent_page_types = ["EventsIndex"]

    # Block the creation of child pages
    subpage_types = []

    class Meta:
        verbose_name = _("Evento")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        parent = self.get_parent()
        context["breadcrumbs"] = [
            {"name": "Eventos", "href": parent.get_url(request=request)},
            {"name": truncatechars(self.title, MAX_TITLE_LENGHT)},
        ]
        return context


class EventsIndex(Page):
    """
    In the CMS Acts like a folder list all Pages of type Event
    For other types of users It renders as a list of events
    """

    template = "main/events/event_list.html"
    # Only allow Events as child pages
    subpage_types = ["EventPage"]

    def __init__(self, *args, **kwargs):
        # importing here to avoid circular imports, because get_wagtailpage_paginated uses the models defined on this file
        from django_src.apps.main.news_event_views import get_wagtailpage_paginated

        super().__init__(*args, **kwargs)
        self.get_paginated_events = get_wagtailpage_paginated(
            PageModel=EventPage, per_page=20
        )

    def serve(self, request):
        # Add support for pagination to this index page
        response = super().serve(request)
        if request.htmx and request.GET:
            context = self.get_context(request)
            html = render_block_to_string(
                block_name="cards",
                template_name="main/events/event_list.html",
                context=context,
            )
            return HttpResponse(html)

        return response

    def get_context(self, request, *args, **kwargs):

        page_number = get_page_number(request)
        context = super().get_context(request, *args, **kwargs)
        context["breadcrumbs"] = [
            {"name": "Eventos"},
        ]

        # Add extra variables and return the updated context
        events = EventPage.objects.child_of(self).live().order_by("-last_published_at")
        context.update(
            self.get_paginated_events(
                page_obj_name="events", page_number=page_number, queryset=events
            )
        )
        return context
