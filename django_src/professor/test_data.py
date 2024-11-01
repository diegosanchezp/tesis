import os
from django_src.test_utils import parse_test_data_args
from shscripts.backup import setup_django
from django_src.settings.wagtail_pages import PROFESSORS_GROUP_NAME


class ProfessorData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete

    Depends on migration django_src/professor/migrations/0002_professor_setup.py
    """

    def __init__(self):
        from django.contrib.auth import get_user_model
        from django_src.professor.models import Professor
        from django.contrib.auth.models import Group

        self.User = get_user_model()
        self.Professor = Professor
        self.Group = Group

        self.professor1_user = self.User(
            username="profesor1",
            first_name="Profesor1",
            last_name="UCV",
            email="profesor1@mail.com",
        )

        self.professor1 = self.Professor(user=self.professor1_user)

        self.professor_group = self.Group.objects.get(name=PROFESSORS_GROUP_NAME)

    def save_profesor_user(self, professor_user):

        professor_user.set_password(os.environ["ADMIN_PASSWORD"])
        professor_user.save()
        professor_user.groups.add(self.professor_group)

    def create(self):
        self.save_profesor_user(self.professor1_user)
        self.professor1.save()

    def get(self):
        """
        Get the objects from the database as they are saved in the database
        useful for adding related things
        """
        self.professor1 = self.Professor.objects.get(
            user__username=self.professor1_user.get_username()
        )

    def get_users(self):
        """
        Fetches the student users from the database
        """

        self.professor1_user = self.User.objects.get(
            username=self.professor1_user.get_username()
        )

    def delete(self):
        self.get_users()

        # Cascade delete of an user deletes the Professor row and everything related to it
        self.professor1_user.delete()


# python -m django_src.professor.test_data --action create
# python -m django_src.professor.test_data --action delete
if __name__ == "__main__":
    setup_django(".")
    args = parse_test_data_args()

    professor_data = ProfessorData()

    if args.action == "create":
        professor_data.create()
    elif args.action == "delete":
        professor_data.delete()
