# The Mentor model is located on the register app
from django.db import models
from django.utils.translation import gettext_lazy as _

from django.urls.base import reverse_lazy

def transition(machine: dict, status: models.TextChoices, event: models.TextChoices):

    try:
        next_state = machine[status][event]
        return next_state
    except KeyError:
        raise TransitionError(
            message=(
                f"Error: no transition defined for state: {status}"
                f"with event: {event}"
            ),
            state=status,
            event=event,
        ) from KeyError

class TransitionError(Exception):
    state: str
    event: str
    def __init__(self, message: str, state: str, event: str) -> None:
        super().__init__(message)
        self.state = state
        self.event = event

class Mentorship(models.Model):

    # The mentor that created the mentorship
    mentor = models.ForeignKey(
        to="register.Mentor",
        on_delete=models.CASCADE,
        related_name="mentorships",
        verbose_name=_("Mentorías"),
    )

    # Name of the mentorship
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nombre"),
    )

    # How many students have completed
    # the mentorship
    num_completed = models.PositiveIntegerField(
        default=0,
    )

    students_enrolled = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        unique_together = [["mentor", "name"]]
        verbose_name = _("Mentoría")
        verbose_name_plural = _("Mentorías")

    def __str__(self) -> str:
        return f"{self.name}"

    def get_request_url(self):
        return reverse_lazy("mentor:request_mentorship", kwargs={"mentorship_pk": self.pk})

    def get_tasks_url(self):
        """
        This urls returns the tasks rendered in html
        """
        return reverse_lazy("mentor:get_tasks", kwargs={"mentorship_pk": self.pk})

    def get_absolute_url(self):
        """
        URL to the mentorship detail view
        """
        return reverse_lazy("mentor:mentorship_detail", kwargs={"mentorship_pk": self.pk})

class MentorshipTask(models.Model):
    """
    MentorshipTask serves as template of tasks that a student has to complete
    """

    name = models.CharField(
        verbose_name=_("Nombre de la tarea"),
        max_length=255,
    )

    mentorship = models.ForeignKey(
        to="Mentorship",
        verbose_name=_("Tarea"),
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    def __str__(self) -> str:
        return f"{self.name}"



class StudentMentorshipTask(models.Model):
    """
    Task assigned to the student
    """

    class Events(models.TextChoices):
        # Student is making progress in task
        PROGRESS = "PROGRESS", _("Progresar")

        COMPLETE = "COMPLETE", _("Completar")
        # Student puts task on TODO state
        PAUSE = "PAUSE", _("Pausar")

    class State(models.TextChoices):
        """
        State of mentorship task
        """

        TODO = "TODO", _("Por hacer")
        IN_PROGRESS = "IN_PROGRESS", _("En progreso")
        COMPLETED = "COMPLETED", _("Completada")

    machine = {
        State.TODO: {
            Events.PROGRESS: State.IN_PROGRESS,
        },
        State.IN_PROGRESS: {
            Events.PAUSE: State.TODO,
            Events.COMPLETE: State.COMPLETED,
        },
        State.COMPLETED: {
            Events.PAUSE: State.TODO,
            Events.PROGRESS: State.IN_PROGRESS,
        },
    }

    student = models.ForeignKey(
        to="register.Student",
        on_delete=models.CASCADE,
        related_name="mentorship_tasks",
        verbose_name=_("Mis tareas de Mentorías"),
    )

    task = models.ForeignKey(
        to="MentorshipTask",
        on_delete=models.CASCADE,
        related_name="student_tasks"
    )

    state = models.CharField(
        max_length=250,
        choices=State.choices,
        default=State.TODO,
    )

    class Meta:
        unique_together = [["student", "task"]]
        verbose_name = _("Tarea de mentoría de estudiantes")
        verbose_name_plural = _("Tareas de mentoría de estudiantes")

    def __str__(self) -> str:
        return f"{self.student} {self.task.name}"

    def transition(self, event: Events) -> None:
        """
        Transition to the next state given an event and the current state
        """
        # Delete the "Completed" history record, before transitioning to the paused state
        if event == self.Events.PAUSE and self.state == self.State.COMPLETED:
            history_q = self.task.mentorship.history.filter(
                student=self.student,
                mentorship=self.task.mentorship,
                state=MentorshipHistory.State.COMPLETED
            )
            if history_q.exists():
                history_q.delete()

        self.state = transition(self.machine, status=self.state, event=event)


def student_mentorship_is_completed(student, mentorship, task_queryset=None):
    """
    Figure out if all tasks are completed
    """
    mentorship_task_num = mentorship.tasks.count()
    if task_queryset is None:
        task_queryset = StudentMentorshipTask.objects.filter(state=StudentMentorshipTask.State.COMPLETED, student=student)
    student_completed_tasks = task_queryset.count()

    return mentorship_task_num == student_completed_tasks

class MentorshipRequest(models.Model):
    """
    When a student wants to enroll into a mentorship
    he has to make a request first.
    """

    class Events(models.TextChoices):
        # Student cancels the request
        REJECT = "REJECT", _("Rechazar")
        CANCEL = "CANCEL", _("Cancelar")
        ACCEPT = "ACCEPT", _("Aceptar")

    class State(models.TextChoices):
        """
        States of the requests
        """

        # Student makes a request
        REQUESTED = "REQUESTED", _("Solicitado")

        # Student can cancel the request (if done by mistake)
        CANCELED = "CANCELED", _("Cancelado")

        # Mentor can reject the request
        REJECTED = "REJECTED", _("Rechazado")

        # Mentor can accept the request
        ACCEPTED = "ACCEPTED", _("Aceptada")

    machine = {
        State.REQUESTED: {
            Events.REJECT: State.REJECTED,
            Events.ACCEPT: State.ACCEPTED,
            Events.CANCEL: State.CANCELED,
        },
    }

    mentorship = models.ForeignKey(
        to="Mentorship",
        on_delete=models.CASCADE,
        related_name="mentorship_requests",
        verbose_name=_("Mentoría"),
    )

    # Student that made the request
    student = models.ForeignKey(
        to="register.Student",
        on_delete=models.CASCADE,
        related_name="mentorship_requests",
        verbose_name=_("Estudiante"),
    )

    status = models.CharField(
        max_length=255,
        verbose_name=_("Estado"),
        choices=State.choices,
        default=State.REQUESTED,
    )

    date = models.DateTimeField(
        verbose_name=_("Fecha del estatus"),
        # Automatically set the field to now every time the object is saved
        auto_now=True,
    )

    class Meta:
        unique_together = [["student", "mentorship"]]
        verbose_name = _("Solicitud de mentoría")
        verbose_name_plural = _("Solicitudes de mentoría")

    def transition(self, event: Events) -> None:
        try:
            next_state = self.machine[self.status][event]
            self.status = next_state
        except KeyError:
            raise TransitionError(
                (
                    f"Error: no transition defined for state: {self.status}"
                    f"with event: {event}"
                )
            ) from KeyError

    def __str__(self) -> str:
        return f"{self.student} {self.status}"

    def get_change_status_url(self):

        if not self.status == self.State.REQUESTED:
            return ""

        return reverse_lazy("mentor:change_mentorship_status", kwargs={"mentorship_req_pk": self.pk})

    def get_readable_status(self):
        """
        Gets the verbose name
        """
        if isinstance(self.status, str):
            return self.State[self.status].label

class MentorshipHistory(models.Model):
    """
    Models the events of a mentorship for a student
    """
    class State(models.TextChoices):
        ACCEPTED = "ACCEPTED", _("Aceptado")
        COMPLETED = "COMPLETED", _("Completado")

    student = models.ForeignKey(
        to="register.Student",
        on_delete=models.CASCADE,
        related_name="mentorship_history",
        verbose_name=_("Estudiante"),
    )

    mentorship = models.ForeignKey(
        to="Mentorship",
        on_delete=models.CASCADE,
        related_name="history",
        verbose_name=_("Mentoría"),
    )

    state = models.CharField(
        choices=State.choices,
        default=State.ACCEPTED,
    )

    date = models.DateTimeField()

    def __str__(self) -> str:
        return f"{self.student.user.first_name} {self.mentorship} {self.state}"

    class Meta:
        verbose_name = _("Historial de mentoría")
        verbose_name_plural = _("Historial de mentorías")


