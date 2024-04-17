from django.urls.base import reverse_lazy
from .utils import get_mentor, is_approved, validate_add_tasks, loggedin_and_approved
from .forms import MentorshipForm, MentorshipTaskFormSet, MentorshipRequestActionForm, get_MentorshipTaskFormSet
from .models import MentorshipRequest, Mentorship, TransitionError, StudentMentorshipTask, MentorshipTask
from django_src.apps.auth.models import User
from django_src.apps.register.models import Student, Mentor
from render_block import render_block_to_string

from django_htmx.middleware import HtmxDetails
from django_htmx.http import trigger_client_event

from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from render_block import render_block_to_string

# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
    user: User

@require_http_methods(["GET", "POST"])
@loggedin_and_approved
@is_approved
def create_mentorship(request: HtmxHttpRequest):
    template_name = "mentor/create_mentorship.html"

    mentor = get_mentor(request.user.username, prefetch_related="")

    context = {
        "mentor": mentor,
    }

    action = request.POST.get("action") or request.GET.get("action")

    if request.method == "POST":

        if request.htmx and action == "validate_add_tasks":
            return validate_add_tasks(request, template_name, "tasks_formset", context, MentorshipTaskFormSet)

        if action == "create":
            mentorship_form = MentorshipForm(data={**request.POST.dict(), "mentor": mentor.pk,})
            mentorship_tasks_form = MentorshipTaskFormSet(data=request.POST)


            if mentorship_form.is_valid() and mentorship_tasks_form.is_valid():

                mentorship = mentorship_form.save()

                tasks = mentorship_tasks_form.save(commit=False)

                for task in tasks:
                    task.mentorship = mentorship
                    task.save()

                # TODO: Make a redirect to the mentorship list view
                return HttpResponseRedirect(redirect_to=reverse_lazy("mentor:my_mentorships"))

            # Some of the forms are invalid
            context["mentorship_form"] = mentorship_form
            context["mentorship_tasks_form"] = mentorship_tasks_form

            # form_html = render_block_to_string(template_name, "forms", context)

            return TemplateResponse(request, template_name, context)


    if request.method == "GET":

        if request.htmx and action == "validate_add_tasks":

            # create a new formset with the TOTAL_FORMS incremented by 1, this adds
            # a new empty form to the set

            mentorship_tasks_form = MentorshipTaskFormSet(data=request.GET)

            # Trigger validation so errors can be populated
            mentorship_tasks_form.is_valid()

            get_data = request.GET.copy()

            total_forms_key = f"{mentorship_tasks_form.prefix}-TOTAL_FORMS"

            new_extra = int(get_data.get(total_forms_key)) + 1

            get_data[total_forms_key] = str(new_extra)

            mentorship_tasks_form = get_MentorshipTaskFormSet(
                extra=new_extra, max_num=new_extra
            )(data=get_data)

            context["mentorship_tasks_form"] = mentorship_tasks_form

            form_html = render_block_to_string(template_name, "tasks_formset", context)
            return HttpResponse(form_html)

        # Default flow: visiting the page to create a mentorship
        mentorship_form = MentorshipForm()
        mentorship_tasks_form = MentorshipTaskFormSet(
            # Set queryset to none, the formset shouldn't include any preexisting instances of the model
            queryset=MentorshipTask.objects.none()
        )

        context["mentorship_form"] = mentorship_form
        context["mentorship_tasks_form"] = mentorship_tasks_form

        return TemplateResponse(request, template_name, context)

@require_http_methods(["GET"])
@loggedin_and_approved
def get_mentorship_tasks(request: HtmxHttpRequest, mentorship_pk: int):
    """
    Returns the tasks of a mentorship so it can be rendered as a modal
    """

    mentorship = get_object_or_404(Mentorship.objects.prefetch_related("tasks"), pk=mentorship_pk)

    tasks = mentorship.tasks.all().order_by("name")

    return TemplateResponse(request, template="mentor/mentorship_tasks.html", context={
        "mentorship": mentorship,
        "tasks": tasks,
    })

@require_http_methods(["POST"])
@loggedin_and_approved
def make_mentorship_request(request: HtmxHttpRequest, mentorship_pk: int):
    """
    A student makes a mentorship request to a mentor
    """

    mentorship = get_object_or_404(Mentorship, pk=mentorship_pk)
    student = get_object_or_404(Student, user__username=request.user.username)
    success_message = success_response(request, target_element_id=f"mentorship-{mentorship.pk}-message")

    mentorship_request = MentorshipRequest(mentorship=mentorship, student=student)
    mentorship_request.save()

    # Return HTML with the next state name on the button

    context = {
        "mentorship": mentorship,
        "mentorship_request": mentorship_request,
        "is_student": True,
        "MentorshipRequest": MentorshipRequest,
    }

    response = TemplateResponse(
        request=request,
        template="mentor/mentorship_card.html",
        context = context,
    )

    # response = HttpResponse(response_html)

    # Send a success message, with a serverside event to htmx
    success_message(message=_("Solicitud creada"), response=response, context=context)

    return response


def message_response(status: int, message_type: str):
    """
    Initial setup for the message response fn
    """

    # Setup the message fn
    message_fn = getattr(messages, message_type)

    # Figure
    def message_response_inner(request, target_element_id: str):
        """
        For setting up the the request of the message
        """

        def twice_inner(message: str, response: HttpResponse | None = None, context: dict = {},):
            """
            This function only takes the message

            - target_element_id: id of the target element where the message should be posioned in the DOM
            - aditional context to be passed for rendering the message
            """
            # Set the message using the django messages framework
            message_fn(request, message)

            # Make an empty response if none is provided
            if response is None:
                response = HttpResponse(status=status)

            # Render the message
            message_html = render_to_string(
                request=request,
                context=context,
                template_name="components/messages.html"
            )

            # Trigger a client side event
            trigger_client_event(
                response=response,
                name=f"render_{message_type}_message",
                params={
                    "message_html": message_html,
                    "target_element_id": target_element_id,
                },
            )

            return response

        return twice_inner
    return message_response_inner

error_message_response = message_response(HttpResponseBadRequest.status_code, "error")
success_response = message_response(HttpResponse.status_code, "success")

@require_http_methods(["POST"])
@loggedin_and_approved
def change_mentorship_status(request, mentorship_req_pk: int):
    """
    A student or a Mentor changes mentorship status
    """


    mentorship_req = get_object_or_404(MentorshipRequest, pk=mentorship_req_pk)
    mentorship = mentorship_req.mentorship

    # Render messages above the mentorship component
    target_element_id = f"mentorship-{mentorship.pk}-message"

    error_response = error_message_response(request, target_element_id=target_element_id)
    success_message = success_response(request, target_element_id=target_element_id)

    student_queryset = Student.objects.filter(user=request.user)
    mentor_queryset = Mentor.objects.filter(user=request.user)

    is_student = student_queryset.exists()
    is_mentor = mentor_queryset.exists()

    action_form = MentorshipRequestActionForm(request.POST)
    success_message_response = None

    if not action_form.is_valid():
        # Todo: leverage django messages framework
        # Say that action is invalid ?
        # Or simply render the invalid form as a response
        return error_response(_("Acción inválida"))

    action = action_form.cleaned_data["action"]

    try:
        mentorship_req.transition(event=action)
    except TransitionError:
        # Todo: message transition error
        return error_response(
            _("Error en el cambio de estado para la acción %(action)s con status %(status)s") % {"action": MentorshipRequest.Events[action].value, "status": MentorshipRequest.State[mentorship_req.status].value }
        )

    if is_mentor:
        # Validate that the mentorship is owned by the mentor
        mentor = mentor_queryset[0]

        # Validations
        if not mentorship_req.mentorship.mentor == mentor:
            # message: can't change a mentorship that isn't created by you
            return error_response(
                _("No puedes cambiar una mentoría que no creaste")
            )

        if action == MentorshipRequest.Events.CANCEL:

            return error_response(
                _("Mentores no pueden cancelar mentorías")
            )

        if action == MentorshipRequest.Events.ACCEPT:
            # When a mentor accepts a mentorship request from a student, create as many entries in StudentMentorshipTask as they are defined in the mentorship
            for task in mentorship.tasks.all():
                m_task = StudentMentorshipTask(
                    student=mentorship_req.student,
                    task=task,
                )
                m_task.save()

        # Mentor accepts/rejects the mentorship requests in a modal displayed mentor/mentorship_detail.html
        response_html = render_block_to_string(
            "mentor/student_info_modal.html", "modal_body_footer", {
                "student": mentorship_req.student,
                "mentorship_request": mentorship_req,
                "MentorshipRequest": MentorshipRequest,
            }
        )
        # We don't need to do anything with the reject action, the transition method above handles it for us
        success_message_response = HttpResponse(response_html)

        # Also, update the mentorship request row table
        trigger_client_event(
            response=success_message_response,
            name="update_mentorship_req_row",
            params={
                "row_id": f"mentor_req_row-{mentorship_req.pk}",
                "row_html": render_to_string(
                    request=request,
                    context={
                        "mentorship_request": mentorship_req,
                    },
                    template_name="mentor/mentorship/request_row.html"
                )
            },
        )


    elif is_student:
        student = student_queryset[0]
        if not mentorship_req.student == student:
            # Invalid Brah you didn't make the request
            return error_response(
                _("Esta mentoría no la solicitaste tu")
            )

        if action == MentorshipRequest.Events.REJECT:
            # student cant approve or reject request
            return error_response(
                _("Un estudiante no puede rechazar mentorías")
            )

        if action == MentorshipRequest.Events.CANCEL:

            response = TemplateResponse(
                request=request,
                template="mentor/mentorship_card.html",
                context = {
                    "mentorship": mentorship,
                    "mentorship_request": mentorship_req,
                    "is_student": is_student,
                    "MentorshipRequest": MentorshipRequest,
                },
            )

            success_message_response = success_message(_("Solicitud de mentoría cancelada"), response=response)

    else:
        # can't do anything you are neither a student or mentor
        return error_response(
            _("No se puede cambiar el estado, no eres estudiante ni mentor")
        )

    # Update the request on the database
    mentorship_req.save()

    # Return success response code 200
    if not success_message_response:
        return error_response(_("Ocurrió un error inesperado"))

    return success_message_response
