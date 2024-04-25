from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods
from django_src.apps.register.models import Student
from django_src.mentor.models import Mentorship, StudentMentorshipTask, TransitionError
from django.shortcuts import get_object_or_404
from django.http.response import Http404, HttpResponse, HttpResponseBadRequest
from django_src.mentor.utils import loggedin_and_approved
from .forms import MentorshipTaskEventForm

@require_http_methods(["GET"])
@loggedin_and_approved
def track_mentorship_task_view(request, mentorship_pk: int, student_pk: int):
    """
    Kanban like view to track Student mentorship Task status
    """
    template="student/track_mentorship_task.html"

    # Student that edits the status of the tasks
    student = get_object_or_404(Student, pk=student_pk)

    mentorship_tasks = StudentMentorshipTask.objects.filter(task__mentorship=mentorship_pk, student=student_pk)

    # If the are no tasks that the student requested for this mentorship return 404
    if not mentorship_tasks.exists():
        return Http404()

    is_student = request.user.is_student
    is_admin = request.user.is_superuser
    is_mentor = request.user.is_mentor

    if is_mentor:
        req_mentor = request.user.mentor
        mentorship = Mentorship.objects.get(pk=mentorship_pk)
        mentorship_mentor = mentorship.mentor
        if mentorship_mentor != req_mentor:
            return HttpResponseBadRequest("Como mentor, no estas autorizado para ver el progreso de este estudiante, ya que no creaste la mentoría.")

    if is_student:
        req_student = request.user.student

        # A student can't see the tasks of another student
        if req_student != student:
            return HttpResponseBadRequest("No autorizado para ver las tareas de la mentoría")

    context = {
        "student": student,
        "is_student": is_student,
        "is_mentor": is_mentor,
        "is_admin": is_admin,
        "Events": StudentMentorshipTask.Events,
        "mentorship_tasks": mentorship_tasks,
        "todo_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.TODO),
        "inprogress_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.IN_PROGRESS),
        "completed_tasks": mentorship_tasks.filter(state=StudentMentorshipTask.State.COMPLETED),
    }

    return TemplateResponse(request, template=template, context=context)

@require_http_methods(["POST"])
@loggedin_and_approved
def change_task_state(request, task_pk: int):
    """
    Change the state of the task
    """

    student_task = get_object_or_404(StudentMentorshipTask, pk=task_pk)
    student = student_task.student
    is_student = request.user.is_student

    if not is_student:
        return HttpResponseBadRequest("Solo estudiantes pueden cambiar el status de la mentoría")

    # If the student is not the one that is changing the state of the task: return 400
    request_student = request.user.student
    if student != request_student:
        return HttpResponseBadRequest("No autorizado para cambiar el status de la mentoría")

    event_validator = MentorshipTaskEventForm(data=request.POST)
    if not event_validator.is_valid():
        return HttpResponseBadRequest("Evento inválido")

    event = event_validator.cleaned_data["event"]

    try:
        student_task.transition(event)
    except TransitionError:
        return HttpResponseBadRequest("Error en el cambio de estado")

    student_task.save()

    return HttpResponse("OK")
