from django.test import TestCase
from django_src.apps.register.models import (
    Student, StudentInterest,
    Mentor, MentorExperience,
    Faculty, Carreer, CarrerSpecialization,
)
from datetime import date
from django.contrib.auth import get_user_model

# ./manage.py test django_src.apps.register.tests.ModelTests.test_student_model
class ModelTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.faculty = Faculty.objects.create(
            name="Ciencias",
        )

        self.computacion = self.faculty.carreers.create(name="Computación")

        self.student_user = User.objects.create(
            username="diego",
            first_name="Diego",
            last_name="Sánchez",
            email="diego@mail.com",
        )

        self.mentor_user = User.objects.create(
            username="pedro",
            first_name="Pedro",
            last_name="Rodriguez",
            email="pedro@mail.com",
        )

        self.student = Student.objects.create(
            user=self.student_user,
            carreer=self.computacion,
        )

    def test_student_model(self):

        ati = CarrerSpecialization.objects.create(
            name="Aplicaciones Tecnología Internet",
        )

        ati.students.add(self.student)

        self.assertEqual(ati.students.count(), 1)
        self.assertEqual(ati.students.first().user.first_name, self.student.user.first_name)

        self.student.interests.create(
            name="Matemáticas",
        )

        self.student.interests.create(
            name="Programación",
        )
        self.assertEqual(self.student.interests.count(),2)
        breakpoint()


    def test_mentor_model(self):
        mentor = Mentor.objects.create(
            user=self.mentor_user,
            carreer=self.computacion,
        )

        # the students to whom the mentor has mentored
        mentor.students.add(self.student)

        self.assertEqual(self.student.mentor_set.count(), 1)
        # These will be used when registering the mentor
        mentor.experiences.create(
            name="Front end developer",
            company="Meta",
            current=False,
            init_year=date(year=2010,month=12,day=1),
            end_year=date(year=2012,month=6,day=12),
            description="Doing frontend things @Meta formerly Facebook",
        )

        mentor.experiences.create(
            name="Front end developer",
            company="Google",
            init_year=date(year=2012,month=6,day=19),
            current=True,
            description="Doing frontend things",
        )
        self.assertEqual(mentor.experiences.count(), 2)

        breakpoint()

