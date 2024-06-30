# python -m django_src.mentor.test_data --action delete

from django.db.utils import IntegrityError
from shscripts.backup import setup_django
from django_src.test_utils import parse_test_data_args
from datetime import datetime

from django_src.apps.register.test_data.mentors import MentorData
from django_src.apps.register.test_data.students import StudentData

class MentorshipData:
    """
    Life cyle (the order you should call the methods)
    1. create
    2. get
    3. delete
    """

    def __init__(self, mentor_data: MentorData, student_data: StudentData):
        from django_src.mentor.models import MentorshipRequest, MentorshipTask, Mentorship, StudentMentorshipTask, MentorshipHistory
        from django_src.apps.main.models import BlogPage, BlogIndex

        self.Mentorship = Mentorship
        self.MentorshipHistory = MentorshipHistory
        self.MentorshipRequest = MentorshipRequest
        self.MentorshipTask = MentorshipTask
        self.StudentMentorshipTask = StudentMentorshipTask
        self.BlogPage = BlogPage
        self.BlogIndex = BlogIndex
        self.student_data = student_data
        self.mentor_data = mentor_data

        self.mentorship1 = Mentorship(
            name="Creación de curriculum",
            mentor=self.mentor_data.mentor1,
        )

        self.m1_task1 = MentorshipTask(name="Escribir las 10 cosas que mas te gustan de tu carrra.", mentorship=self.mentorship1)

        self.m1_task2 = MentorshipTask(name="Escribe los 3 lenguajes de programación que más te gustan", mentorship=self.mentorship1)

        self.m1_task3 = MentorshipTask(name="Leer libro sobre modelado de datos", mentorship=self.mentorship1)

        self.student_request = self.MentorshipRequest(
            student=self.student_data.student,
            mentorship=self.mentorship1,
            status=self.MentorshipRequest.State.ACCEPTED,
        )

        self.student_request2 = self.MentorshipRequest(
            student=self.student_data.unapproved_student,
            mentorship=self.mentorship1,
            status=self.MentorshipRequest.State.REQUESTED,
        )


    def create(self):
        # Get the mentors from db
        self.mentor_data.get()
        self.student_data.get()

        try:
            # Save first the mentorship, the task need it
            self.mentorship1.mentor = self.mentor_data.mentor1
            self.mentorship1.save()
        except Exception as e:
            # Todo if mentor doesn't exists then ??
            e.add_note("save the mentor_data first to database")
            raise

        self.m1_task1.save()
        self.m1_task2.save()
        self.m1_task3.save()

        # Create an accepted student request

        self.student_request.mentorship=self.mentorship1
        self.student_request.student=self.student_data.student
        self.student_request.save()

        self.student_request2.mentorship=self.mentorship1
        self.student_request2.student=self.student_data.unapproved_student
        self.student_request2.save()


        # Create tasks for a student, since the request was accepted
        for task in self.mentorship1.tasks.all():
            m_task = self.StudentMentorshipTask(
                student=self.student_data.student,
                task=task,
            )
            m_task.save()

        self.MentorshipHistory(
            student=self.student_data.student,
            mentorship=self.mentorship1,
            state=self.MentorshipHistory.State.ACCEPTED,
            date=datetime(year=2024, month=6, day=29, hour=13, minute=32)
        ).save()

    def get(self):
        """
        Get the objects from the database as they are saved in the database
        useful for adding related things
        """
        self.mentor_data.get()
        self.mentorship1 = self.Mentorship.objects.get(name=self.mentorship1.name, mentor__user__username=self.mentorship1.mentor.user.get_username())
        self.m1_task1 = self.MentorshipTask.objects.get(name=self.m1_task1.name, mentorship=self.mentorship1)
        self.m1_task2 = self.MentorshipTask.objects.get(name=self.m1_task2.name, mentorship=self.mentorship1)
        self.m1_task3 = self.MentorshipTask.objects.get(name=self.m1_task3.name, mentorship=self.mentorship1)
        self.student_request = self.MentorshipRequest.objects.get(student=self.student_data.student, mentorship=self.mentorship1)
        self.student_request2 = self.MentorshipRequest.objects.get(student=self.student_data.unapproved_student, mentorship=self.mentorship1)

    def delete(self):
        self.get()
        self.mentorship1.delete()

# python -m django_src.mentor.test_data --action create
# python -m django_src.mentor.test_data --action delete

if __name__ == "__main__":
    setup_django(".")
    args = parse_test_data_args()

    mentorship_data = MentorshipData(MentorData(), StudentData())

    if args.action == "create":
        mentorship_data.create()
    elif args.action == "delete":
        mentorship_data.delete()
