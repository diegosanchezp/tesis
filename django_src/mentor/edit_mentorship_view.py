from .utils import get_mentor, is_approved, validate_add_tasks
from .models import Mentorship, MentorshipTask
from .forms import MentorshipForm
from .mentorship_detail_view import render_mentorship_info

from render_block import render_block_to_string

from django.urls.base import reverse_lazy
from django.forms import modelformset_factory
from django.http.response import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

MentorshipTaskFormSet = modelformset_factory(
    model=MentorshipTask,
    exclude=["mentorship"],
)


@require_http_methods(["DELETE"])
@login_required
@is_approved
def delete_task(request, task_pk: int):
    """
    Delete a task from a mentorship
    """
    mentor = get_mentor(request.user.username, prefetch_related="mentorships")
    task = get_object_or_404(MentorshipTask, pk=task_pk)
    mentorship = task.mentorship

    # If the mentor doesn't own the task, return 400
    if mentorship.mentor != mentor:
        return HttpResponseBadRequest()

    task.delete()

    form_html = render_block_to_string("mentor/forms/edit_mentorship_form.html", "tasks_formset", {
        "mentorship_tasks_form": MentorshipTaskFormSet(queryset=mentorship.tasks.all())
    })

    # Todo send success message ?
    return HttpResponse(form_html)


@require_http_methods(["POST"])
@login_required
@is_approved
def delete_mentorship(request, mentorship_pk: int):

    mentor = get_mentor(request.user.username, prefetch_related="mentorships")
    mentorship = get_object_or_404(mentor.mentorships, pk=mentorship_pk)

    # If the mentor doesn't own the task, return 400
    if mentorship.mentor != mentor:
        return HttpResponseBadRequest('You are not the owner of this mentorship')

    mentorship.delete()

    return HttpResponseRedirect(
        redirect_to=reverse_lazy(
            "mentor:my_mentorships"
        )
    )


@require_http_methods(["POST", "GET"])
@login_required
@is_approved
def edit_mentorship_view(request, mentorship_pk: int):
    """
    View for editing a mentorship and its tasks
    actions: delete_task
    """

    template_name = "mentor/forms/edit_mentorship_form.html"

    mentor = get_mentor(request.user.username, prefetch_related="mentorships")
    mentorship = get_object_or_404(mentor.mentorships, pk=mentorship_pk)

    MentorshipTaskFormSet = modelformset_factory(
        model=MentorshipTask,
        exclude=["mentorship"],
    )

    action = request.POST.get("action") or request.GET.get("action")

    if not request.htmx:
        return HttpResponseBadRequest('request not made with htmx')

    if request.method == "GET":
        if action == "get_edit_form":
            mentorship_form = MentorshipForm(instance=mentorship)
            mentorship_tasks_form = MentorshipTaskFormSet(queryset=mentorship.tasks.all())

            response = TemplateResponse(request, template_name, {
                "mentorship_form": mentorship_form,
                "mentorship": mentorship,
                "mentorship_tasks_form": mentorship_tasks_form,
            })
            return response

    if request.method == "POST":
        if action == "validate_add_tasks":
            return validate_add_tasks(
                request, template_name, "tasks_formset", {"mentorship": mentorship},
                MentorshipTaskFormSet
            )

        mentorship_form = MentorshipForm(
            instance=mentorship,
            data={**request.POST.dict(), "mentor": mentor.pk,}
        )

        mentorship_tasks_form = MentorshipTaskFormSet(
            data=request.POST,
            queryset=mentorship.tasks.all(),
        )

        if mentorship_form.is_valid() and mentorship_tasks_form.is_valid():

            mentorship = mentorship_form.save()
            tasks = mentorship_tasks_form.save(commit=False)

            for task in tasks:
                if task.mentorship_id is None:
                    task.mentorship = mentorship
                task.save()

            form_html = render_mentorship_info(mentor, mentorship)
            return HttpResponse(form_html)

        # The form is invalid, return the form and task formset with the errors
        form_html = render_block_to_string(template_name, "tasks_formset", {
            "mentorship_form": mentorship_form,
            "mentorship": mentorship,
            "mentorship_tasks_form": mentorship_tasks_form,
        })
        return HttpResponseBadRequest(form_html)

    return HttpResponseBadRequest("Invalid action")


