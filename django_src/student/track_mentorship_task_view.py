from django.template.response import TemplateResponse
from django_src.apps.register.models import Student
from django_src.mentor.models import StudentMentorshipTask, TransitionError
from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse, HttpResponseBadRequest

from .forms import MentorshipTaskEventForm

def get_student(user):
    """
    Get student object from user
    """
    return get_object_or_404(Student,user=user)

def track_mentorship_task_view(request, mentorship_pk: int):
    """
    Kanban like view to track Student mentorship Task status
    """
    template="student/track_mentorship_task.html"

    student = get_student(request.user)
    mentorship_tasks = student.mentorship_tasks.filter(task__mentorship=mentorship_pk)

    context = {
        "student": student,
        "mentorship_tasks": mentorship_tasks,
        "todo_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.TODO),
        "inprogress_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.IN_PROGRESS),
        "completed_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.COMPLETED),
    }

    return TemplateResponse(request, template=template, context=context)

def change_task_state(request, task_pk: int):
    """
    Change the state of the task
    """

    student = get_student(request.user)
    student_task = student.mentorship_tasks.get(pk=task_pk)

    event_validator = MentorshipTaskEventForm(data=request.POST)
    if not event_validator.is_valid():
        return HttpResponseBadRequest("Evento inválido")
    event = event_validator.cleaned_data["event"]

    try:
        student_task.transition(event)
    except TransitionError:
        return HttpResponseBadRequest("Error en el cambio de estado")

    return HttpResponse("OK")
