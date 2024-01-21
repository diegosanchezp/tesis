from datetime import date

import django.db
from django.db.models.query import QuerySet

from django_src.apps.register.test_utils import TestCaseWithData

from django_src.apps.register.models import (
    CarrerSpecialization,
    Mentor, MentorExperience,
    InterestTheme,
    ThemeSpecProCarreer,
)

# ./manage.py test --keepdb django_src.apps.register.test_models.ModelTests
class ModelTests(TestCaseWithData):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()


    def setUp(self):
        super().setUp()


    # ./manage.py  test --keepdb django_src.apps.register.test_models.ModelTests.test_student_model
    def test_student_model(self):

        self.computacion.carrerspecialization_set.add(
            self.ati
        )

        self.ati.students.add(self.student)

        self.assertEqual(self.ati.students.count(), 1)
        self.assertEqual(self.ati.students.first().user.first_name, self.student.user.first_name)

        mates = self.student.interests.create(
            name="Matemáticas",
        )

        programacion = self.student.interests.create(
            name="Programación",
        )

        self.computacion.interest_themes.add(mates)
        self.computacion.interest_themes.add(programacion)
        self.assertGreater(self.computacion.interest_themes.count(),0)

        self.assertEqual(self.student.interests.count(),2)


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


    # ./manage.py test --keepdb django_src.apps.register.test_models.ModelTests.test_exp_uniqueness
    def test_exp_uniqueness(self):

        mentor = Mentor.objects.create(
            user=self.mentor_user,
            carreer=self.computacion,
        )

        exp1 = MentorExperience(
            mentor=mentor,
            name="Full stack developer",
            company="Google",
            init_year=date(2010,1,1),
            end_year=date(2011,1,1),
            current=False,
            description="Full Stack Dev @ Google",
        )

        exp1.save()

        exp2 = MentorExperience(
            mentor=mentor,
            name="Full stack developer",
            company="Google",
            init_year=date(2010,1,1),
            end_year=date(2011,1,1),
            current=False,
            description="Full Stack Dev @ Google",
        )

        with self.assertRaises(django.db.IntegrityError):
            exp2.save()

    def test_bulk(self):

        interests = InterestTheme.objects.bulk_create(
            [
                InterestTheme(name="Matemáticas"),
                InterestTheme(name="Programación"),
            ]
        )

        self.computacion.interest_themes.add(*interests)
        self.assertTrue(self.computacion.interest_themes.count(), 2)


    # def test_upload_datascript(self):
    #     create_carreers()

# ./manage.py test --keepdb django_src.apps.register.test_models.TestProCarreerRegister
class TestProCarreerRegister(TestCaseWithData):
    """
    Test the integration of the ProCarrer Model with all the models of the register app
    """

    # ./manage.py test --keepdb django_src.apps.register.test_models.TestProCarreerRegister.test_select_related
    def test_select_related(self):
        """
        Test the select_related method
        """

        careers_spec = CarrerSpecialization.objects.select_related("career__faculty").prefetch_related("pro_carreers_match")

        # If i loop the careers queryset, the faculty should be cached
        for career_spec in careers_spec:
            # pro_carreers_match is of type GenericRelation. I Don't know if this is cached
            # by the prefetch_related
            pro_carreers_matches: QuerySet[ThemeSpecProCarreer] = career_spec.pro_carreers_match.all()

            self.assertIn("career", career_spec._state.fields_cache)
            self.assertIn("faculty", career_spec.career._state.fields_cache)
            if career_spec.name == self.ati.name:
                self.assertEqual(pro_carreers_matches.count(), 2)




