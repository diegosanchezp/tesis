from pathlib import Path
import os
from datetime import date

from shscripts.backup import (
    setup_django
)

from .test_data.mentors import MentorData
from django_src.pro_carreer.test_data import create_pro_carreers

from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.apps import apps
from django.apps.registry import Apps
from django.contrib.auth import get_user_model
from django.db import transaction

from dataclasses import dataclass


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

def mentors(apps: Apps):
    """
    Create two mentors
    so it can be checked that no mentors can edit each other posts
    """

    Mentor = apps.get_model(app_label="register", model_name="Mentor")
    Carreer = apps.get_model(app_label="register", model_name="Carreer")
    Group = apps.get_model("auth", model_name="Group")
    User = get_user_model()
    BlogIndex = apps.get_model(app_label="main", model_name="BlogIndex")
    BlogPage = apps.get_model(app_label="main", model_name="BlogPage")

    with transaction.atomic():
        mentor1_user = User.objects.create(
            username="mentor1@mail.com",
            first_name="Mentor1",
            last_name="Test",
            email="mentor1@mail.com",
        )
        mentor1_user.set_password(os.environ["ADMIN_PASSWORD"])

        mentor1 = Mentor.objects.create(
            user=mentor1_user,
            carreer=Carreer.objects.get(name="Computación"),
        )

        mentor1_user.set_password(os.environ["ADMIN_PASSWORD"])
        mentor1_user.save()

        mentor1.experiences.create(
            name="Front end developer",
            company="Meta",
            current=False,
            init_year=date(year=2010,month=12,day=1),
            end_year=date(year=2012,month=6,day=12),
            description="Doing frontend things @Meta, formerly Facebook",
        )

        mentor2_user = User.objects.create(
            username="mentor2@mail.com",
            first_name="Mentor2",
            last_name="Test",
            email="mentor2@mail.com",
        )

        mentor2_user.set_password(os.environ["ADMIN_PASSWORD"])
        mentor2_user.save()

        mentor2 = Mentor.objects.create(
            user=mentor2_user,
            carreer=Carreer.objects.get(name="Computación"),
        )
        mentor2.experiences.create(
            name="Full Stack Dev",
            company="Google",
            current=False,
            init_year=date(year=2013,month=12,day=1),
            end_year=date(year=2015,month=6,day=12),
            description="Full Stack dev @Google",
        )
        # Add the users to the mentors group
        mentors_group = Group.objects.get(name='Mentores')

        mentor1_user.groups.add(mentors_group)
        mentor2_user.groups.add(mentors_group)

        # Create two blogs for the mentors
        blog_index = BlogIndex.objects.get()

        blog_index.add_child(instance=BlogPage(
            owner=mentor1_user,
            title="Blog Mentor 1",
            slug="blog-mentor-1",
            # content="<p>Mentor 1 Blog Post's</p>",
        ))

        blog_index.add_child(instance=BlogPage(
            owner=mentor2_user,
            title="Blog Mentor 2",
            slug="blog-mentor-2",
            # content="<p>Mentor 2 Blog Post's</p>",
        ))

        from django_src.apps.register.models import Mentor
        from django_src.apps.main.models import BlogIndex

        @dataclass
        class ModelList:
            mentor1: Mentor
            mentor2: Mentor
            blog_index: BlogIndex


        return ModelList(
            mentor1=mentor1,
            mentor2=mentor2,
            blog_index=blog_index,
        )

def reset_mentors(apps: Apps):
    """
    Delete all mentors
    """

    with transaction.atomic():
        User = get_user_model()
        BlogPage = apps.get_model(app_label="main", model_name="BlogPage")

        mentors_emails = ["mentor1@mail.com", "mentor2@mail.com"]

        # Delete all of the blog posts owned by the mentors
        BlogPage.objects.filter(owner__email__in=mentors_emails).delete()

        mentors = User.objects.filter(
            email__in=mentors_emails,
        )
        mentors.delete()

def upload_data():
    """
    Put here all of the functions that create carreers
    """
    carreer_list = create_carreers()
    students(apps)
    mentors(apps)
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
