import os
from datetime import date, timedelta
from pathlib import Path
import argparse

from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.conf import settings

from shscripts.backup import setup_django

class MentorData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):

        from django_src.apps.register.models import Mentor, RegisterApprovalStates
        from django_src.mentor.models import Mentorship, MentorshipTask
        from django_src.pro_carreer.models import ProCarreerExperience
        from django.contrib.contenttypes.models import ContentType


        self.User = get_user_model()
        self.MentorModel = Mentor
        self.RegisterApprovalStates = RegisterApprovalStates
        self.ProCarreerExperience = ProCarreerExperience
        self.Mentorship = Mentorship
        self.MentorshipTask = MentorshipTask
        self.ContentType = ContentType

        self.mentor1_user = self.User(
            username="mentor1",
            first_name="John",
            last_name="Doe",
            email="jonh_doe@mail.com",
        )

        self.mentor2_user = self.User(
            username="mentor2",
            first_name="Juan",
            last_name="David",
            email="juan_david@mail.com",
        )

        self.mentor1 = Mentor(
            user=self.mentor1_user,
            voucher=SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            )

        )

        self.mentor2 = Mentor(
            user=self.mentor2_user,
            voucher=SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            )
        )



    def save_mentor(self, mentor):
        try:
            mentor.set_password(os.environ["ADMIN_PASSWORD"])
            mentor.save()
        except IntegrityError:
            self.delete_mentor(mentor)
            mentor.save()

    def delete_mentor(self, mentor_user):

        # Deleting the user triggers casacade delete
        self.User.objects.get(username=mentor_user.username).delete()

    def create(self, computacion, full_stack_dev):
        """
        Insert objects into the database, should only be called once.
        if user is already in the database, it will be deleted and reinserted

        computacion: apps.register.models.Carreer
        """

        self.mentor_type = self.ContentType.objects.get_for_model(self.MentorModel)

        from django.contrib.auth.models import Group

        self.save_mentor(self.mentor1_user)
        self.save_mentor(self.mentor2_user)

        self.admin_user = self.User.objects.get(
            username=settings.ADMIN_USERNAME,
        )
        mentors_group = Group.objects.get(name='Mentores')

        mentor1 = self.mentor1
        mentor1.carreer = computacion
        mentor1.save()

        # Approval for mentor1
        self.mentor1_user.my_approvals.create(
            admin=self.admin_user,
            state=self.RegisterApprovalStates.APPROVED,
            user_type=self.mentor_type,
        )

        mentor1 = self.mentor1

        mentor1.experiences.create(
            name="Full stack developer",
            company="Meta",
            current=False,
            init_year=date(year=2010,month=12,day=1),
            end_year=date(year=2012,month=6,day=12),
            description="Doing frontend things @Meta, formerly Facebook",
        )
        init_year=date(year=2015, month=1, day=1)


        self.mentor1_user.groups.add(mentors_group)
        self.mentor2_user.groups.add(mentors_group)

        self.ProCarreerExperience.objects.create(
            mentor=mentor1,
            pro_carreer=full_stack_dev,
            experience="Es una carrera  en la que vas aprendiendo a través de los años, basado en mi experiencia personal, existarán algunos días en los que tienes que tener 100% de disponibilidad. Otras cosas que me gustaría mencionar son ...",
            rating=5,
            company="Google",
            init_year=init_year,
            end_year=init_year + timedelta(days=365*5),
        )

        # ------ Mentor 2 ------ #

        self.mentor2.carreer = computacion
        self.mentor2.save()

        self.ProCarreerExperience.objects.create(
            mentor=self.mentor2,
            pro_carreer=full_stack_dev,
            experience="I have been working as a full stack developer for 5 years, and you basically do everything, from frontend to backend to devops",
            rating=4,
            company="Yahoo",
            init_year=date(year=2015, month=1, day=1),
            end_year=date(year=2020, month=1, day=1),
        )


        # Professional experience timeline

        end_year_mentor2 = date(year=2015,month=6,day=12)

        self.mentor2.experiences.create(
            name="Full Stack Dev",
            company="Google",
            current=False,
            init_year=date(year=2013,month=12,day=1),
            end_year=end_year_mentor2,
            description="Full Stack developer, did some bleeding edge backend things and frontend things",
        )
        self.mentor2.experiences.create(
            name="VR developer",
            company="Meta",
            current=True,
            init_year=end_year_mentor2,
            description="Doing VR things @Meta, formerly Facebook",
        )

        # Approval for mentor2
        self.mentor2_user.my_approvals.create(
            admin=self.admin_user,
            state=self.RegisterApprovalStates.APPROVED,
            user_type=self.mentor_type,
        )

    def get(self):
        """
        Get the objects from the database
        """
        self.mentor1_user = self.User.objects.get(username=self.mentor1_user.username)
        self.mentor1 = self.MentorModel.objects.get(user=self.mentor1_user)
        self.mentor2_user = self.User.objects.get(username=self.mentor2_user.username)
        self.mentor2 = self.MentorModel.objects.get(user=self.mentor2_user)

    def delete(self):
        """
        Deletes all mentors
        """
        self.delete_mentor(self.mentor1_user)
        self.delete_mentor(self.mentor2_user)


# python -m django_src.apps.register.test_data.mentors --action create
# python -m django_src.apps.register.test_data.mentors --action delete

if __name__ == "__main__":
    setup_django(".")

    from django_src.apps.register.models import Carreer
    from django_src.pro_carreer.models import ProfessionalCarreer


    # Beging parser setup
    parser = argparse.ArgumentParser(
        description="Reset database script"
    )

    parser.add_argument(
        "--action",
        help="Delete uploaded data or create it",
        choices=["create", "delete"],
        default="create",
    )

    args = parser.parse_args()

    computacion = Carreer.objects.get(name="Computación")
    full_stack_dev = ProfessionalCarreer.objects.get(title="Full stack Developer")

    mentor_data = MentorData()

    if args.action == "create":
        mentor_data.create(computacion, full_stack_dev)
    elif args.action == "delete":
        mentor_data.delete()
