from pathlib import Path

from shscripts.backup import (
    setup_django
)

from .test_data.mentors import MentorData
from .test_data.students import StudentData
from django_src.pro_carreer.test_data import create_pro_carreers

from django.apps import apps
from django.apps.registry import Apps
from django.contrib.auth import get_user_model
from django.db import transaction

from dataclasses import dataclass


app_label = "register"
# python -m django_src.apps.register.upload_data

def create_interest_themes(carreer):
    """
    Create interest themes for a carrer
    """

    InterestTheme = apps.get_model(app_label, "InterestTheme")

    interests = InterestTheme.objects.bulk_create(
        [
            InterestTheme(name="Matemáticas"),
            InterestTheme(name="Programación"),
            InterestTheme(name="HTML"),
            InterestTheme(name="Javascript"),
            InterestTheme(name="CSS"),
            InterestTheme(name="C++"),
            InterestTheme(name="UI/UX"),
            InterestTheme(name="Trabajo en equipo"),
            InterestTheme(name="Gestion de Recursos"),
            InterestTheme(name="BPM"),
        ]
    )

    carreer.interest_themes.add(*interests)

def create_carreers():
    with transaction.atomic():
        Faculty = apps.get_model(app_label, "Faculty")

        agronomia = Faculty.objects.create(
            name="Agronomía",
        )

        agronomia.carreers.create(name="Agronomía")

        arquitectura = Faculty.objects.create(
            name="Arquitectura y Urbanismo",
        )

        arquitectura.carreers.create(name="Arquitectura")

        ciencias = Faculty.objects.create(
            name="Ciencias",
        )

        geoquimica = ciencias.carreers.create(name="Geoquímica")
        matematica = ciencias.carreers.create(name="Matemática")
        quimica = ciencias.carreers.create(name="Química")
        biologia = ciencias.carreers.create(name="Biología")
        computacion = ciencias.carreers.create(name="Computación")

        computacion_specialization =[
            "Aplicaciones Tecnología Internet",
            "Inteligencia artificial",
            "Base de datos",
            "Ingeniería de Software",
            "Computación Gráfica",
            "Sistemas de información",
            "Sistemas distribuidos y paralelos",
            "Calculo Científico",
            "Modelos matemáticos",
            "Tecnologías educativas",
            "Tecnologías en Comunicaciones y Redes de Computadoras"
        ]

        for carrerspecialization in computacion_specialization:
            computacion.carrerspecialization_set.create(
                name=carrerspecialization,
            )

        create_interest_themes(computacion)

        ciencias.carreers.create(name="Física")

        faces = Faculty.objects.create(
            name="Ciencias Económicas y Sociales",
        )
        faces.carreers.create(name="Administración y Contaduría")
        faces.carreers.create(name="Antropología")
        faces.carreers.create(name="Estadística y Ciencias Actuariales")
        faces.carreers.create(name="Economía")
        faces.carreers.create(name="Estudios Internacionales")
        faces.carreers.create(name="Sociología")
        faces.carreers.create(name="Trabajo Social")

        derecho = Faculty.objects.create(
            name="Ciencias Jurídicas y Políticas",
        )

        veterinaria = Faculty.objects.create(
            name="Ciencias Veterinarias",
        )

        farmacia = Faculty.objects.create(
            name="Farmacia",
        )

        humanidades = Faculty.objects.create(
            name="Humanidades y Educación",
        )

        humanidades.carreers.create(name="Artes" )
        humanidades.carreers.create(name="Bibliotecología y Archivología")
        humanidades.carreers.create(name="Comunicación Social")
        humanidades.carreers.create(name="Educación")
        humanidades.carreers.create(name="Filosofía")
        humanidades.carreers.create(name="Geografía")
        humanidades.carreers.create(name="Historia")
        humanidades.carreers.create(name="Idiomas Modernos")
        humanidades.carreers.create(name="Letras")
        humanidades.carreers.create(name="Psicología")

        ingenieria = Faculty.objects.create(
            name="Ingeniería",
        )

        medicina = Faculty.objects.create(
            name="Medicina",
        )

        odontologia = Faculty.objects.create(
            name="Odontología",
        )

        from django_src.apps.register.models import Carreer, Faculty

        @dataclass
        class ModelList:
            computacion: Carreer
            geoquimica: Carreer
            matematica: Carreer
            quimica: Carreer
            biologia: Carreer
            ingenieria: Faculty
            medicina: Faculty
            odontologia: Faculty

        return ModelList(
            geoquimica=geoquimica,
            matematica=matematica,
            quimica=quimica,
            biologia=biologia,
            computacion=computacion,
            ingenieria=ingenieria,
            medicina=medicina,
            odontologia=odontologia,
        )

def upload_data():
    """
    Put here all of the functions that create carreers
    """
    carreer_list = create_carreers()

    student_data = StudentData()
    student_data.create()

    mentor_data = MentorData()
    pro_career_list = create_pro_carreers()

    mentor_data.create(
        computacion=carreer_list.computacion,
        full_stack_dev=pro_career_list.fullstack_dev,
    )


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    setup_django(BASE_DIR)

    upload_data()

if __name__ == "__main__":
    main()
