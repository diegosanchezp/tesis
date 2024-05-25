"""
Functions for Uploading or Deleting all of the testing data
"""

from dataclasses import dataclass
from pathlib import Path
import argparse
from django_src.apps.register.test_data.mentors import MentorData

from django_src.apps.register.test_data.students import StudentData
from django_src.apps.main.test_data.news import NewsData
from django_src.apps.main.test_data.events import EventsData
from django_src.mentor.test_data import MentorshipData
from django_src.mentor.test_blog_data import MentorBlogData
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from django.apps import apps
from django.apps.registry import Apps
from django_src.apps.register.upload_data import (
    MentorData,
    create_carreers,
)
from django_src.pro_carreer.test_data import (
    ProCarreerData,
    create_pro_interes_themes,
    delete_pro_interes_themes,
)
from shscripts.backup import setup_django

# python -m django_src.apps.main.dev_data upload
# python -m django_src.apps.main.dev_data reset


def dev_pages(apps: Apps):
    """
    Wagtail pages
    """

    # Importing models, can't do top level import because app regitry is not loaded

    # from .models import  HomePage, HeroSection
    # from wagtail.models import Site
    # from wagtail.images.models import Image

    HomePage = apps.get_model("main", model_name="HomePage")
    HeroSection = apps.get_model("main", model_name="HeroSection")
    Image = apps.get_model("wagtailimages", model_name="Image")
    Site = apps.get_model("wagtailcore", model_name="Site")

    User = get_user_model()

    admin = User.objects.get(username=settings.ADMIN_USERNAME)

    with transaction.atomic():
        img_phone_mockup, created = Image.objects.get_or_create(
            title="phone-mockup",
            file="original_images/phone-mockup_wP3cGMj.png",
            uploaded_by_user=admin,
        )

        img_logo_egresados, created = Image.objects.get_or_create(
            title="Logo egresados",
            file="original_images/logo_egresados_ucv.jpg",
            uploaded_by_user=admin,
        )

        img_impulsar_carrera, created = Image.objects.get_or_create(
            title="Impulsar carrera",
            file="original_images/impulsar_carrera.png",
            uploaded_by_user=admin,
        )

        img_event, created = Image.objects.get_or_create(
            title="Event",
            file="original_images/event.png",
            uploaded_by_user=admin,
        )

        colaboration_img, created = Image.objects.get_or_create(
            title="colaboration",
            file="original_images/colaboration.webp",
            uploaded_by_user=admin,
        )

        # img_=Image.objects.get_or_create(
        #     title="",
        #     file="",
        #     uploaded_by_user=admin,
        # )

        # Update home page
        home_page = HomePage.objects.get(slug="root_home")

        home_page.header_image = img_logo_egresados
        home_page.owner = admin
        home_page.title = "Home"
        home_page.live = True
        # apperently locking the page blocks the view live button, thus can't generate an url
        # home_page.locked = True # Don't let other users edit this page
        home_page.header_text = "La Asociación de Egresados y Amigos de la UCV, te invitan a registrarte en la nueva plataforma de mentorías."
        home_page.header_cta = "Registrarme"

        # Add hero sections to home page
        home_page.hero_sections = [
            HeroSection(
                sort_order=1,
                page=home_page,
                title="Encuentra talento profesional",
                description="El temprano siglo XX, aparte del terremoto de 1900, no trajo para Venezuela cambios significativos en lo relativo a la dirección hacia la modernidad y la democracia, pues al contrario de ello, la Revolución Liberal Restauradora de 1899, insertó en el poder a los tiránicos caudillos andinos hasta 1935, profundizándose con los Generales Cipriano Castro y Juan Vicente Gómez, los mecanismos de opresión, como lo fueron la clausura de la UCV, la cárcel, el exilio, la tortura y la muerte contra sus opositores, llegándose hasta unos límites inéditos. Con base a la experiencia de los tiempos de Guzmán y Crespo, la Universidad Central respondió nuevamente con manifestaciones cívicas de protesta de intensidad creciente, desde la recordada “Sacrada” de 1901, las protestas y huelga universitaria contra las Reformas del Rector Guevara Rojas en 1912, el apoyo golpe cívico/militar de 1919, la rebelión de los Tranvías Eléctricos de 1921 y finalmente la revuelta estudiantil de 1928.",
                image=img_phone_mockup,
            ),
            HeroSection(
                sort_order=2,
                page=home_page,
                title="Accede a eventos exclusivos",
                description="El conflicto emancipador que abarca para Venezuela el periodo entre los años de 1810 a 1821, comprometió a la Universidad de Caracas a liderizar un proceso, civil antes que militar, que junto al protagonismo del Ayuntamiento de Caracas, se desarrolló principalmente como un movimiento reivindicador de la soberanía venezolana en un ámbito de gradual evolución política desde la actitud conservadora de los derechos de Fernando VII el 19 de abril en 1810 hasta la declaración plena de la independencia republicana el 5 de julio de 1811",
                image=img_event,
            ),
            HeroSection(
                sort_order=3,
                page=home_page,
                image=colaboration_img,
                title="Colabora con la UCV",
                description="En manos de los civiles munícipes y universitarios se levantó la Primera República y, dolorosamente, en manos militares se perdió en 1812 con eventos como los de de Puerto Cabello, Coro y San Mateo. Por ello, en la sesión del Claustro Pleno Universitario del 09 de julio de 1811 la Universidad de Caracas se incorporó, bajo la presidencia del Rector Dr. José Vicente Machillanda, a reconocer y respaldar: “la independencia absoluta de la Provincia de Venezuela de toda otra potestad que no emane de la voluntad libre y general de sus pueblos”, emitiéndose un Acta que reposa hoy en el Archivo Histórico de la UCV, cuyo gran valor jurídico y político llevó, el 30 de septiembre de1812, a que el Capitán Domingo Monteverde, jefe militar de las fuerzas realistas que reconquistaron Caracas, presionara al Claustro universitario para tachar de sus libros el contenido pro independentista de la trascendente Acta",
            ),
            HeroSection(
                sort_order=0,
                title="Impulsa el inicio de tu carrera profesional",
                description="El nacimiento mismo de la Universidad de Caracas, el 22 de diciembre de 1721, representó uno de los acontecimientos de mayor importancia de todo el periodo colonial venezolano, comprendido entre los siglos XVI y principios del XIX, tratándose éste de un proceso muy complejo, que significaba principalmente el que la sociedad colonial venezolana había alcanzado un grado de madurez interna que le permitía aspirar y obtener del Rey Felipe V la aprobación de la elevación del Colegio Seminario de Santa Rosa de Lima hacia el estatus de Real Universidad de Caracas (luego también Pontificia por Bula de Inocencio XIII de 1722)",
                image=img_impulsar_carrera,
            ),
            # HeroSection(
            #     sort_order=0,
            #     page=home_page,
            #     title="",
            #     description="",
            #     image=,
            # )
        ]

        home_page.save()

        # Modify the default provided by Wagtail
        try:
            site = Site.objects.get(is_default_site=True, hostname="localhost", port=80)
            site.hostname = "127.0.0.1"
            site.port = 8000
            site.root_page = home_page
            site.save()
        except Site.DoesNotExist:
            # Don't bother updating the site because it is already updated
            pass
        except IntegrityError:
            # Delete the wagtail provided site beacuse it is already updated
            pass


def reset_dev_pages(apps):

    with transaction.atomic():
        User = get_user_model()

        Image = apps.get_model("wagtailimages", model_name="Image")
        admin = User.objects.get(username=settings.ADMIN_USERNAME)
        # The bad thing about deleting the images is that it deletes them from the file system
        img_phone_mockup = Image.objects.get(
            title="phone-mockup",
            file="original_images/phone-mockup_wP3cGMj.png",
            uploaded_by_user=admin,
        ).delete()

        img_logo_egresados = Image.objects.get(
            title="Logo egresados",
            file="original_images/logo_egresados_ucv.jpg",
            uploaded_by_user=admin,
        ).delete()

        img_impulsar_carrera = Image.objects.get(
            title="Impulsar carrera",
            file="original_images/impulsar_carrera.png",
            uploaded_by_user=admin,
        ).delete()

        img_event = Image.objects.get(
            title="Event",
            file="original_images/event.png",
            uploaded_by_user=admin,
        ).delete()

        colaboration_img, created = Image.objects.get(
            title="colaboration",
            file="original_images/colaboration.webp",
            uploaded_by_user=admin,
        ).delete()


# Data dependency
# -> Right hand function depends on the created data of the left hand function
#


def upload_dev_data():

    carreer_list = create_carreers()

    student_data = StudentData()
    mentor_data = MentorData()
    mentor_blog_data = MentorBlogData(mentor_data)
    mentorship_data = MentorshipData(mentor_data, student_data)

    student_data.create()
    pro_career_list = ProCarreerData()
    pro_career_list.create()
    mentor_data.create(
        computacion=carreer_list.computacion,
        full_stack_dev=pro_career_list.fullstack_dev,
    )
    mentorship_data.create()
    mentor_blog_data.create()
    dev_pages(apps)
    create_pro_interes_themes()

    news_data = NewsData()
    events_data = EventsData()
    news_data.create()
    events_data.create()


def reset():
    student_data = StudentData()
    mentorship_data = MentorshipData(MentorData(), StudentData())
    mentor_data = MentorData()
    news_data = NewsData()
    events_data = EventsData()

    student_data.delete()
    delete_pro_carreers()
    mentor_data.delete()
    mentorship_data.delete()
    reset_dev_pages(apps)
    delete_pro_interes_themes()
    news_data.delete()
    events_data.delete()

    # The bad thing about deleting the images is that it deletes them from the file system
    # reset_dev_pages(apps)


# python -m django_src.apps.main.dev_data upload
def main():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    # Beging parser setup
    parser = argparse.ArgumentParser(description="Upload data for development tasks")

    parser.add_argument(
        "action",
        choices=["upload", "reset"],
        help="upload: upload the the database, reset: remove uploaded data",
    )

    args = parser.parse_args()
    # Ensure app registry is loaded
    setup_django(BASE_DIR)

    if args.action == "upload":
        upload_dev_data()
    elif args.action == "reset":
        reset()


if __name__ == "__main__":
    main()
