from pathlib import Path

from wagtail.rich_text import RichText
from django_src.business.test_data.businesses import BusinessData
from django_src.settings.wagtail_pages import jobs_index_path

from shscripts.backup import setup
from django_src.test_utils import parse_test_data_args
from django_src.apps.register.test_data.interest_themes import InterestThemeData


class JobsOfferData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(
        self, business_data: BusinessData, interest_themes_data: InterestThemeData
    ):
        from django_src.business.models import JobOffer, JobOfferIndex, JobOfferInterest

        self.interest_themes = interest_themes_data

        self.JobOfferInterest = JobOfferInterest
        self.JobOffer = JobOffer
        self.JobOfferIndex = JobOfferIndex

        self.business_data = business_data

        # The job index was create by data migration 0002_jobssetup
        self.job_offer_index = JobOfferIndex.objects.get(path=jobs_index_path)

        self.python_remote_job = self.JobOffer(
            owner=business_data.businees1_user,
            title="Desarrollador Python desde casa",
            slug="desarrollador-python-desde-casa",
            workplace=JobOffer.JobType.REMOTE,
            linkedin_link="https://www.linkedin.com/jobs/view/3933987479",
            description=[
                (
                    "paragraph",
                    RichText(
                        # fmt: off
                        """
                        <p>
                        Reconocida como la empresa de desarrollo de software líder en América, nuestro cliente ofrece una modalidad 100% remota y un excelente entorno de trabajo en el que los empleados pueden prosperar, trabajar en equipos multiculturales, con horarios flexibles y un sinfín de oportunidades de crecimiento.
                        </p>
                        <b>Acerca del puesto:</b>
                        <p>
                            Buscamos Python Senior Developers para unirse a nuestro equipo de Desarrollo y participar en diferentes proyectos formados por equipos multiculturales distribuidos por todo el mundo. Buscamos personas proactivas, jugadoras de equipo apasionadas por la programación en este lenguaje y orientadas a brindar la mejor experiencia al usuario final. Se trata de una excelente oportunidad para aquellos profesionales que busquen desarrollarse en una de las empresas de mayor crecimiento del sector.
                            Estos desarrolladores se enfrentarán a numerosos retos técnicos, por lo que deberán utilizar tecnologías actuales, involucrarse en el mundo móvil, aplicaciones web, dispositivos, etc.
                        </p>
                        """
                        # fmt: on
                    ),
                ),
            ],
            first_published_at="2024-05-27T00:27:18.507Z",
            last_published_at="2024-05-27T00:27:18.507Z",
        )

    def create(self):
        self.business_data.get()
        self.interest_themes.get()

        self.python_remote_job.owner = self.business_data.businees1_user
        self.python_remote_job_page = self.job_offer_index.add_child(
            instance=self.python_remote_job
        )
        self.python_remote_job = self.JobOffer.objects.get(
            pk=self.python_remote_job_page.id
        )

        self.JobOfferInterest.objects.create(
            job_offer=self.python_remote_job,
            interest=self.interest_themes.python,
        )

        self.JobOfferInterest.objects.create(
            job_offer=self.python_remote_job,
            interest=self.interest_themes.programacion,
        )

    def get(self):
        self.python_remote_job = self.JobOffer.objects.get(
            slug=self.python_remote_job.slug
        )

    def delete(self):
        self.get()
        self.python_remote_job.delete()


# python -m django_src.business.test_data.joboffer --action create
# python -m django_src.business.test_data.joboffer --action delete

if __name__ == "__main__":

    setup(Path("."))
    args = parse_test_data_args()
    job_offer_data = JobsOfferData(
        business_data=BusinessData(), interest_themes_data=InterestThemeData()
    )

    if args.action == "create":
        job_offer_data.create()
    elif args.action == "delete":
        job_offer_data.delete()
