import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from shscripts.backup import setup
from django_src.test_utils import parse_test_data_args


class BusinessData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):
        from django_src.business.models import Business

        self.User = get_user_model()
        self.Business = Business

        self.businees1_user = self.User(
            username="business1",
            first_name="Aviatto",
            last_name="Commodore",
            email="business@aviatto.com",
        )

        self.businees1 = self.Business(
            user=self.businees1_user,
            description="Reconocida como la empresa de desarrollo de software líder en América, nuestro cliente ofrece una modalidad 100% remota y un excelente entorno de trabajo en el que los empleados pueden prosperar, trabajar en equipos multiculturales, con horarios flexibles y un sinfín de oportunidades de crecimiento.",
            web_page="https://diegosanchezp.github.io/",
        )

    def get_user(self, business_user):
        return self.User.objects.get(username=business_user.username)

    def save_user(self, user):
        try:
            user.set_password(os.environ["ADMIN_PASSWORD"])
            user.save()
        except IntegrityError:
            self.delete_user(user)
            user.save()

    def get_business(self, username: str):
        return self.Business.objects.get(user__username=username)

    def delete_user(self, business_user):

        # Deleting the user triggers casacade delete
        self.get_user(business_user).delete()

    def create(self):
        self.save_user(self.businees1_user)
        self.businees1_user = self.get_user(self.businees1_user)

        self.businees1.user = self.businees1_user
        self.businees1.save()
        self.businees1 = self.get_business(self.businees1_user.username)

    def get(self):
        self.businees1_user = self.get_user(self.businees1_user)
        self.businees1 = self.get_business(self.businees1_user.username)

    def delete(self):
        self.get()
        self.delete_user(self.businees1_user)


# python -m django_src.business.test_data.businesses --action create
# python -m django_src.business.test_data.businesses --action delete

if __name__ == "__main__":

    setup(Path("."))
    args = parse_test_data_args()
    business_data = BusinessData()

    if args.action == "create":
        business_data.create()
    elif args.action == "delete":
        business_data.delete()
