from dataclasses import dataclass
from django.db.models import Q
from wagtail.rich_text import RichText

from pathlib import Path

from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup

# from django_src.settings.wagtail_pages import pro_carreer_index_path


def create_pro_interes_themes():
    """
    Creates matches between interest themes and professional carreers
    Important: This function depends on the execution of django_src/apps/register/upload_data.py.create_interest_themes
    """

    from .models import ProfessionalCarreer
    from django_src.apps.register.models import (
        InterestTheme,
        ThemeSpecProCarreer,
        CarrerSpecialization,
    )

    ati = CarrerSpecialization.objects.get(name="Aplicaciones Tecnología Internet")

    frontend_dev = ProfessionalCarreer.objects.get(title="Frontend Developer")
    fullstack_dev = ProfessionalCarreer.objects.get(title="Full stack Developer")

    html_theme, created = InterestTheme.objects.get_or_create(
        name="HTML",
    )

    css_theme, created = InterestTheme.objects.get_or_create(
        name="CSS",
    )

    # Relate html to frontend development
    html_theme.pro_carreers_match.create(
        weight="10",
        pro_career=frontend_dev,
    )

    # Relate css to frontend development
    css_frontend_dev = css_theme.pro_carreers_match.create(
        weight="10",
        pro_career=frontend_dev,
    )

    # Relate css to full development
    css_fullstack = css_theme.pro_carreers_match.create(
        weight="8",
        pro_career=fullstack_dev,
    )

    # Put weight 10 (high correlation) to frontend_dev and fullstack_dev
    ati_frontend_dev = ati.pro_carreers_match.create(
        weight="10",
        pro_career=frontend_dev,
        content_object=ati,
    )

    ati_fullstack_dev = ati.pro_carreers_match.create(
        weight="10",
        pro_career=fullstack_dev,
        content_object=ati,
    )

    @dataclass
    class ModelList:
        html_theme: InterestTheme
        css_theme: InterestTheme
        css_frontend_dev: ThemeSpecProCarreer
        css_fullstack: ThemeSpecProCarreer
        ati_frontend_dev: ThemeSpecProCarreer
        ati_fullstack_dev: ThemeSpecProCarreer

    return ModelList(
        html_theme=html_theme,
        css_theme=css_theme,
        css_frontend_dev=css_frontend_dev,
        css_fullstack=css_fullstack,
        ati_frontend_dev=ati_frontend_dev,
        ati_fullstack_dev=ati_fullstack_dev,
    )


def delete_pro_interes_themes():
    """
    Inverse function of create_pro_interes_themes
    """

    from .models import ProfessionalCarreer
    from django_src.apps.register.models import InterestTheme, ThemeSpecProCarreer

    frontend_dev = ProfessionalCarreer.objects.get(title="Frontend Developer")
    fullstack_dev = ProfessionalCarreer.objects.get(title="Full stack Developer")

    html_theme = InterestTheme.objects.get(
        name="HTML",
    )

    css_theme = InterestTheme.objects.get(
        name="CSS",
    )
    del_query = Q(pro_career=frontend_dev) | Q(pro_carreer=fullstack_dev)
    html_theme.pro_carreers_match.filter(del_query).delete()
    css_theme.pro_carreers_match.filter(del_query).delete()


class ProCarreerData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):
        # Importing here will suck for performance but it's the only way to have type hints
        # and avoid the app registry not loaded error
        # see https://copyprogramming.com/howto/should-i-import-inside-a-function-python
        # section "Import at module level or at function level?"

        from .models import ProCarreerIndex, ProfessionalCarreer

        self.ProCarreerIndex = ProCarreerIndex
        self.ProfessionalCarreer = ProfessionalCarreer

        # Create by migration 0002_setup_professions
        self.pro_career_index = self.ProCarreerIndex.objects.get(slug="profesiones")

        self.frontend_dev = ProfessionalCarreer(
            title="Frontend Developer",
            short_description="Makes WEB GUI stuff",
            slug="frontend-developer",
            content=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                        <p>
                        Un desarrollador web frontend es un profesional especializado en la creación y diseño de la parte visual y la interacción de un sitio web. Sus responsabilidades incluyen la escritura de código en lenguajes como HTML, CSS y JavaScript para desarrollar la interfaz de usuario y la experiencia del usuario en un sitio web. Además, los desarrolladores frontend suelen colaborar estrechamente con diseñadores web y desarrolladores backend para garantizar la funcionalidad y la estética del sitio. Es fundamental que un desarrollador web frontend esté al tanto de las últimas tendencias y tecnologías en el campo para crear sitios web atractivos, receptivos y funcionales
                        </p>
                        """
                        # fmt: on
                    ),
                )
            ],
        )

        self.fullstack_dev = ProfessionalCarreer(
            title="Full stack Developer",
            short_description="Makes WEB GUIs & codes backend services",
            slug="full-stack-developer",
            content=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                        <p>Un desarrollador full stack es un profesional que tiene conocimientos y habilidades en ambos lados del desarrollo web: frontend y backend. Sus principales responsabilidades incluyen:</p>
                        <h2>Desarrollo Frontend</h2>
                        <ul>
                            <li>Escribir código HTML, CSS y JavaScript para crear la interfaz de usuario y la experiencia del usuario.</li>
                        <li>Implementar diseños receptivos y accesibles.</li><li>Integrar APIs y servicios backend en la aplicación frontend.</li>
                        </ul>
                        <h2>Desarrollo Backend</h2>
                            <ul><li >Diseñar y desarrollar APIs y servicios backend utilizando lenguajes como Python, Ruby, Java, PHP, etc.</li>
                            <li >Implementar lógica de negocio y reglas de validación.</li><li>Interactuar con bases de datos para almacenar y recuperar datos.</li>
                        </ul>
                        """
                        # fmt: on
                    ),
                )
            ],
        )

    def create(self):
        self.fullstack_dev = self.pro_career_index.add_child(
            instance=self.fullstack_dev
        )
        self.frontend_dev = self.pro_career_index.add_child(instance=self.frontend_dev)

    def get(self):
        self.frontend_dev = self.ProfessionalCarreer.objects.get(
            slug=self.frontend_dev.slug
        )
        self.fullstack_dev = self.ProfessionalCarreer.objects.get(
            slug=self.fullstack_dev.slug
        )

    def delete(self):
        self.get()
        self.fullstack_dev.delete()
        self.frontend_dev.delete()


# python -m django_src.pro_carreer.test_data --action create
# python -m django_src.pro_carreer.test_data --action delete

if __name__ == "__main__":
    setup(Path("."))
    args = parse_test_data_args()
    pro_carreer_data = ProCarreerData()

    if args.action == "create":
        pro_carreer_data.create()
    elif args.action == "delete":
        pro_carreer_data.delete()
