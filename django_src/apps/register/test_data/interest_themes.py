from pathlib import Path

from shscripts.backup import setup
from django_src.test_utils import parse_test_data_args


class InterestThemeData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self):
        from django_src.apps.register.models import InterestTheme

        self.InterestTheme = InterestTheme

        self.matematicas = InterestTheme(name="Matemáticas")
        self.programacion = InterestTheme(name="Programación")
        self.html = InterestTheme(name="HTML")
        self.javascript = InterestTheme(name="Javascript")
        self.css = InterestTheme(name="CSS")
        self.cplusplus = InterestTheme(name="C++")
        self.uiux = InterestTheme(name="UI/UX")
        self.trabajo_en_equipo = InterestTheme(name="Trabajo en equipo")
        self.gestion_de_recursos = InterestTheme(name="Gestion de Recursos")
        self.bpm = InterestTheme(name="BPM")
        self.python = InterestTheme(name="Python")

    def create(self):
        self.matematicas.save()
        self.programacion.save()
        self.html.save()
        self.javascript.save()
        self.css.save()
        self.cplusplus.save()
        self.uiux.save()
        self.trabajo_en_equipo.save()
        self.gestion_de_recursos.save()
        self.bpm.save()
        self.python.save()

    def get(self):
        self.matematicas = self.InterestTheme.objects.get(name=self.matematicas.name)
        self.programacion = self.InterestTheme.objects.get(name=self.programacion.name)
        self.html = self.InterestTheme.objects.get(name=self.html.name)
        self.javascript = self.InterestTheme.objects.get(name=self.javascript.name)
        self.css = self.InterestTheme.objects.get(name=self.css.name)
        self.cplusplus = self.InterestTheme.objects.get(name=self.cplusplus.name)
        self.uiux = self.InterestTheme.objects.get(name=self.uiux.name)
        self.trabajo_en_equipo = self.InterestTheme.objects.get(
            name=self.trabajo_en_equipo.name
        )
        self.gestion_de_recursos = self.InterestTheme.objects.get(
            name=self.gestion_de_recursos.name
        )
        self.bpm = self.InterestTheme.objects.get(name=self.bpm.name)
        self.python = self.InterestTheme.objects.get(name=self.python.name)

    def get_all_interests(self):
        self.get()
        self.all_interests = [
            self.matematicas,
            self.programacion,
            self.html,
            self.javascript,
            self.css,
            self.cplusplus,
            self.uiux,
            self.trabajo_en_equipo,
            self.gestion_de_recursos,
            self.bpm,
            self.python,
        ]
        return self.all_interests

    def delete(self):
        self.get()
        self.matematicas.delete()
        self.programacion.delete()
        self.html.delete()
        self.javascript.delete()
        self.css.delete()
        self.cplusplus.delete()
        self.uiux.delete()
        self.trabajo_en_equipo.delete()
        self.gestion_de_recursos.delete()
        self.bpm.delete()
        self.python.delete()


# python -m django_src.apps.register.test_data.interest_themes --action create
# python -m django_src.apps.register.test_data.interest_themes --action delete

if __name__ == "__main__":

    setup(Path("."))
    args = parse_test_data_args()
    job_offer_data = InterestThemeData()

    if args.action == "create":
        job_offer_data.create()
    elif args.action == "delete":
        job_offer_data.delete()
