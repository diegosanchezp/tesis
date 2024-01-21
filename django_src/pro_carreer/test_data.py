from dataclasses import dataclass
from django.db.models import Q

def create_pro_carreers():
    """
    Django App registry must have been loaded before calling this function
    """

    # Importing here will suck for performance but it's the only way to have type hints
    # and avoid the app registry not loaded error
    # see https://copyprogramming.com/howto/should-i-import-inside-a-function-python
    # section "Import at module level or at function level?"

    from .models import ProCarreerIndex, ProfessionalCarreer

    @dataclass
    class ModelList:
        """
        Just a list of models instances to be created
        """
        pro_career_index: ProCarreerIndex
        frontend_dev: ProfessionalCarreer
        fullstack_dev: ProfessionalCarreer

    # m_ stands for model class

    pro_career_index = ProCarreerIndex.objects.get(slug="profesiones")

    frontend_dev = pro_career_index.add_child(
        instance=ProfessionalCarreer(
            title="Frontend Developer",
            short_description="Makes WEB GUI stuff",
        )
    )

    fullstack_dev  = pro_career_index.add_child(
        instance=ProfessionalCarreer(
            title="Full stack Developer",
            short_description="Makes WEB GUIs & codes backend services",
        )
    )

    model_list = ModelList(
        pro_career_index=pro_career_index,
        frontend_dev=frontend_dev,
        fullstack_dev=fullstack_dev,
    )

    return model_list

def delete_pro_carreers():

    from .models import ProfessionalCarreer

    frontend_dev = ProfessionalCarreer.objects.get(title="Frontend Developer")
    fullstack_dev = ProfessionalCarreer.objects.get(title="Full stack Developer")
    frontend_dev.delete()
    fullstack_dev.delete()

def create_pro_interes_themes():
    """
    Creates matches between interest themes and professional carreers
    Important: This function depends on the execution of django_src/apps/register/upload_data.py.create_interest_themes
    """

    from .models import ProfessionalCarreer
    from django_src.apps.register.models import InterestTheme, ThemeSpecProCarreer, CarrerSpecialization

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
        weight="10", pro_career=frontend_dev,
    )

    # Relate css to frontend development
    css_frontend_dev = css_theme.pro_carreers_match.create(
        weight="10", pro_career=frontend_dev,
    )

    # Relate css to full development
    css_fullstack = css_theme.pro_carreers_match.create(
        weight="8", pro_career=fullstack_dev,
    )


    # Put weight 10 (high correlation) to frontend_dev and fullstack_dev
    ati_frontend_dev = ati.pro_carreers_match.create(
        weight="10", pro_career=frontend_dev,
        content_object=ati,
    )


    ati_fullstack_dev = ati.pro_carreers_match.create(
        weight="10", pro_career=fullstack_dev,
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

