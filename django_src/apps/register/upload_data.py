from pathlib import Path
import os

from shscripts.backup import (
    setup_django
)

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.apps import apps
from django.apps.registry import Apps
from django.contrib.auth import get_user_model
from django.db import transaction



app_label = "register"
# python -m django_src.apps.register.upload_data

def create_student(
        User, Student, RegisterApprovals,
        ContentType,
        computacion
):
    """
    Creates an approved student with interests

    Depends on register data migration
    """

    from django_src.apps.register.models import RegisterApprovalStates

    student_type = ContentType.objects.get_for_model(Student)

    admin_user = User.objects.get(
        username=settings.ADMIN_USERNAME,
    )

    student_user = User.objects.create(
        username="diego",
        first_name="Diego",
        last_name="Sánchez",
        email="diego@mail.com",
    )

    student_user.set_password(os.environ["ADMIN_PASSWORD"])
    student_user.save()

    student = Student.objects.create(
        user=student_user,
        carreer=computacion,
        voucher=SimpleUploadedFile(
            name="profile_pic.jpg",
            content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
            content_type="image/jpeg",
        )
    )


    student_approval = RegisterApprovals.objects.create(
        user=student_user,
        user_type=student_type,
        admin=admin_user,
        state=RegisterApprovalStates.APPROVED,
    )

    unapproved_student_user = User.objects.create(
        username="unapproved_student",
        first_name="Unapproved",
        last_name="Student",
        email="unapproved_student@mail.com",
    )

    unapproved_student = Student.objects.create(
        user=unapproved_student_user,
        carreer=computacion,
        voucher=SimpleUploadedFile(
            name="profile_pic.jpg",
            content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
            content_type="image/jpeg",
        )
    )

    unapproved_student_approval = RegisterApprovals.objects.create(
        user=unapproved_student_user,
        user_type=student_type,
        state=RegisterApprovalStates.WAITING,
    )

    return (
        student_user, student, student_approval,
        unapproved_student_user, unapproved_student, unapproved_student_approval
    )

def delete_student(User):
    student_user = User.objects.get(username="diego")
    unapproved_student = User.objects.get(username="unapproved_student")

    # Cascade deletes Student
    student_user.delete()
    unapproved_student.delete()

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

        ciencias.carreers.create(name="Geoquímica")
        ciencias.carreers.create(name="Matemática")
        ciencias.carreers.create(name="Química")
        ciencias.carreers.create(name="Biología")
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

def students(apps: Apps, delete=False):
    """
    Creates the student
    Depends on create_carreers
    """
    User = get_user_model()
    Carreer = apps.get_model(app_label="register", model_name="Carreer")
    Student = apps.get_model(app_label="register", model_name="Student")
    RegisterApprovals = apps.get_model(app_label="register", model_name="RegisterApprovals")
    ContentType = apps.get_model(app_label="contenttypes", model_name="ContentType")

    computacion = Carreer.objects.get(name="Computación")

    if not delete:
        create_student(User, Student, RegisterApprovals, ContentType, computacion)
    else:
        delete_student(User)

def upload_data():
    """
    Put here all of the functions that create carreers
    """
    create_carreers()
    students(apps)


def main():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

    setup_django(BASE_DIR)

    upload_data()

if __name__ == "__main__":
    main()
