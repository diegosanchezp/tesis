from typing import Literal, cast
from django import forms
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django_src.apps.register.models import Mentor, Student

from render_block import render_block_to_string
from django_htmx.http import HttpResponseClientRedirect

from .forms import StudentForm, UserCreationForm, MentorForm, QueryForm, get_MentorExperienceFormSet
from .views import step_urls

def get_steps_urls(carreer: str, profile: str):
    url_kwargs = {
        "name": carreer,
    }

    if profile == QueryForm.MENTOR:

        return {
            **step_urls,
            "add_exp": reverse_lazy("register:add_exp")
        }

    elif profile == QueryForm.ESTUDIANTE:

        return {
            **step_urls,
            "specialization": reverse_lazy(
                "register:select_specialization",
                kwargs=url_kwargs,
            ),
            "select_themes": reverse_lazy(
                "register:select_themes",
                kwargs=url_kwargs,
            )
        }
    else:
        return step_urls

def get_Mentor_context(request, action: Literal["initial", "create_mentor"], base_context: dict):

    MentorExperienceFormSet = get_MentorExperienceFormSet()

    if action == "create_mentor":

        context = {
            **base_context,
            "entity_form": MentorForm(data=request.POST, files=request.FILES),
            "exp_formset": MentorExperienceFormSet(data=request.POST),
        }
        return context

    if action == "initial":
        context = {
            **base_context,
            "entity_form": MentorForm(),
            "formset_prefix": MentorExperienceFormSet().prefix,
        }
        return context

    return base_context


def get_Student_context(request, action: Literal["initial", "create_student"], base_context: dict):

    # When the user is submitting the user data, plus all data of the previous steps
    if action == "create_student":

        form_kwargs = {
            "data": request.POST,
            "files": request.FILES,
        }

        return {
            **base_context,
            "user_form": UserCreationForm(**form_kwargs),
            "entity_form": StudentForm(**form_kwargs),
        }

    if action == "initial":

        return {
            **base_context,
            "no_spec": "no_spec" in request.GET,
            "entity_form": StudentForm(),
        }


def get_context(
    request,
    action: Literal["initial", "create_student", "create_mentor"],
):
    """
    action:
    - initial is for a simple get request, when the user is first visiting this step, a.k.a "default" state
    """

    query_form = QueryForm(request.GET or request.POST)

    # Always needed context for this view
    context = {
        "query_form": query_form,
    }

    # Don't continue adding more context if the query form is not valid
    if not query_form.is_valid():
        return context

    profile = query_form.cleaned_data["profile"]
    carreer = query_form.cleaned_data["carreer"]

    context.update(
        {
            "carrer": carreer,
            "profile": profile,
            "step_urls": get_steps_urls(
                carreer, profile
            ),
        }
    )

    user_form = UserCreationForm()

    if request.POST:
        user_form = UserCreationForm(data=request.POST, files=request.FILES)

    context.update({
        "user_form": user_form,
    })

    if profile == QueryForm.ESTUDIANTE:
        context.update(get_Student_context(request, action=action, base_context=context))
    if profile == QueryForm.MENTOR:
        context.update(get_Mentor_context(request, action=action, base_context=context))

    return context

def create_student(user, student_form: StudentForm) -> Student:

    # Create an instance of the student object but don't save it to DB
    student = student_form.save(commit=False)

    # Relate the user instance to the student
    student.user = user

    # Finally save to database
    student.save()

    return student

def create_mentor(user, mentor_form: MentorForm, experience_form) -> Mentor:
    """
    """

    # Create an instance of the mentor object but don't save it to DB
    mentor = mentor_form.save(commit=False)

    # Relate the user instance to the mentor
    mentor.user = user

    # Save the mentor to the database
    mentor.save()

    # Save and relate the experiences to the mentor
    experiences = experience_form.save(commit=False)

    for experience in experiences:
        experience.mentor = mentor
        experience.save()

    return mentor


def create_user(
    user_form: UserCreationForm,
):

    # Create the user
    user = user_form.save(commit=False)
    user.username = user.email
    user.save()

    return user

# trying out function base views for probably the most complex view of this register module
def complete_profile_view(request):
    template_name = 'register/complete_profile.html'


    if request.method == "POST" and request.htmx:

        context = get_context(
            request, action=request.POST.get("action"),
        )

        # Cast is used for type hints
        # https://stackoverflow.com/questions/71845596/python-typing-narrowing-type-from-function-that-returns-a-union
        user_form = cast(UserCreationForm,context["user_form"])
        entity_form = cast(forms.ModelForm,context["entity_form"])
        query_form = cast(forms.ModelForm,context["query_form"])

        # ---- case: both forms are valid ---- #
        if query_form.is_valid() and user_form.is_valid() and entity_form.is_valid():

            entity = None

            if isinstance(entity_form, StudentForm):
                user = create_user(user_form)
                entity = create_student(user, entity_form)

            if isinstance(entity_form, MentorForm):
                exp_formset = context["exp_formset"]
                if exp_formset.is_valid():
                    breakpoint()
                    user = create_user(user_form)
                    entity = create_mentor(user, entity_form, exp_formset)

            if entity:
                # put here a success message using django messages
                # Change this to a redirect ?
                return HttpResponseClientRedirect(redirect_to=reverse_lazy("register:success"))

        # ---- case: forms are invalid ---- #

        form_html = render_block_to_string(template_name, "form", context)

        # Make a response with the rendered new list of themes
        htmx_reponse = HttpResponse(form_html)

        return htmx_reponse


    if request.method == "GET":
        context = get_context(
            request, action="initial",
        )
        return TemplateResponse(request, template_name, context)
