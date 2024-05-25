import os
from pathlib import Path

from django.db.utils import IntegrityError
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup_django

class StudentData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get <-- get the created data
    3. delete
    """

    def __init__(self):
        from django_src.apps.register.models import RegisterApprovalStates, RegisterApprovals
        from django.contrib.contenttypes.models import ContentType
        from django.contrib.auth import get_user_model
        from django_src.apps.register.models import Student, Carreer

        self.User = get_user_model()
        self.Student = Student
        self.RegisterApprovalStates = RegisterApprovalStates
        self.RegisterApprovals = RegisterApprovals
        self.ContentType = ContentType

        self.student_type = ContentType.objects.get_for_model(Student)

        self.computacion = Carreer.objects.get(name="Computación")

        self.admin_user = self.User.objects.get(
            username=settings.ADMIN_USERNAME,
        )

        self.student_user = self.User(
            username="diego",
            first_name="Diego",
            last_name="Sánchez",
            email="diego@mail.com",
        )

        self.student = Student(
            user=self.student_user,
            carreer=self.computacion,
            voucher=SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            )
        )

        self.student_approval = RegisterApprovals(
            user=self.student_user,
            user_type=self.student_type,
            admin=self.admin_user,
            state=RegisterApprovalStates.APPROVED,
        )

        self.unapproved_student_user = self.User(
            username="unapproved_student",
            first_name="Unapproved",
            last_name="Student",
            email="unapproved_student@mail.com",
        )

        self.unapproved_student = Student(
            user=self.unapproved_student_user,
            carreer=self.computacion,
            voucher=SimpleUploadedFile(
                name="profile_pic.jpg",
                content=open(str(Path(settings.MEDIA_ROOT_TEST) / "jpeg_example.jpg"), "rb").read(),
                content_type="image/jpeg",
            )
        )

        self.unapproved_student_approval = RegisterApprovals(
            user=self.unapproved_student_user,
            user_type=self.student_type,
            state=RegisterApprovalStates.WAITING,
            admin=self.admin_user,
        )

    def save_student_user(self, student_user):
        try:
            student_user.set_password(os.environ["ADMIN_PASSWORD"])
            student_user.save()
        except IntegrityError as integrity_error:
            if "unique constraint" in integrity_error.args[0]:

                print(student_user.username, "already exists deleting it and creating it again.")
                # if the user already exists, delete it and create it again
                student_user_db = self.User.objects.get(username=student_user.get_username())
                student_user_db.delete()
                student_user.save()

    def create(self):
        self.save_student_user(self.student_user)
        self.student.save()
        self.student_approval.save()

        self.save_student_user(self.unapproved_student_user)
        self.unapproved_student.save()
        self.unapproved_student_approval.save()

    def get_users(self):
        """
        Fetches the student users from the database
        """
        self.student_user = self.User.objects.get(username=self.student_user.get_username())
        self.unapproved_student_user = self.User.objects.get(username=self.unapproved_student_user.get_username())

    def get(self):
        """
        Get the objects from the database as they are saved in the database
        useful for adding related things
        """
        self.get_users()
        self.student = self.Student.objects.get(user=self.student_user)
        self.student_approval = self.RegisterApprovals.objects.get(
            user=self.student_user,
            user_type=self.student_type,
            admin=self.admin_user,
        )

        self.unapproved_student = self.Student.objects.get(user=self.unapproved_student_user)
        self.unapproved_student_approval = self.RegisterApprovals.objects.get(
            user=self.unapproved_student_user,
            user_type=self.student_type,
            admin=self.admin_user,
        )

    def delete(self):
        self.get_users()

        # Cascade deletes Student and everything related to it
        self.student_user.delete()
        self.unapproved_student_user.delete()

# python -m django_src.apps.register.test_data.students --action create
# python -m django_src.apps.register.test_data.students --action delete

if __name__ == "__main__":
    setup_django(".")
    args = parse_test_data_args()
    student_data = StudentData()

    if args.action == "create":
        student_data.create()
    elif args.action == "delete":
        student_data.delete()
