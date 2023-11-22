from typing import Literal, TypedDict, cast
from django.http import HttpResponse
from django.http.response import HttpResponseNotAllowed
from django.template.response import TemplateResponse
from django.urls import reverse_lazy

from render_block import render_block_to_string
from django_htmx.http import HttpResponseClientRedirect

from .forms import StudentForm, UserCreationForm
from .views import step_urls

def get_steps_urls(carreer: str):
    url_kwargs = {
        "name": carreer,
    }
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

def get_context(
    request,
    action: Literal["initial", "create_student"],
):

    # Always needed context for this view

    carreer = None

    if request.GET.get("carreer"):
        carreer = request.GET.get("carreer")
    if request.POST.get("carreer"):
        carreer = request.POST.get("carreer")
    if carreer is None:
        return


    context = {
        "step_urls": get_steps_urls(
            carreer
        ),
        "no_spec": "no_spec" in request.GET,
    }

    if action == "initial":
        context["user_form"] = UserCreationForm()
        context["student_form"] = StudentForm()
        context["urlCarrer"] = request.GET.get("carreer")
        return context

    if action == "create_student":

        form_kwargs = {
            "data": request.POST,
            "files": request.FILES,
        }

        context["user_form"] = UserCreationForm(**form_kwargs)
        context["student_form"] = StudentForm(**form_kwargs)

        return context

def create_entities(
    user_form: UserCreationForm,
    student_form: StudentForm,
):

    # Create the user
    user = user_form.save(commit=False)
    user.username = user.email
    user.save()

    # Create an instance of the student object but don't save it to DB
    student = student_form.save(commit=False)

    # Relate the user instance to the student
    student.user = user

    # Finally save to database
    student.save()

    return {
        "user": user,
        "student": student,
    }

# trying out function base views for probably the most complex view of this register module
def complete_profile_view(request):
    template_name = 'register/complete_profile.html'

    if request.method == "POST" and request.htmx:

        context = get_context(request, action=request.POST.get("action"))
        if context is None:
            return HttpResponseNotAllowed("Invalid action")

        # Cast is used for type hints
        # https://stackoverflow.com/questions/71845596/python-typing-narrowing-type-from-function-that-returns-a-union
        user_form = cast(UserCreationForm,context["user_form"])
        student_form = cast(StudentForm,context["student_form"])

        # ---- case: both forms are valid ---- #
        if user_form.is_valid() and student_form.is_valid():
            create_entities(user_form,student_form)

            # put here a success message using django messages
            # Change this to a redirect ?
            return HttpResponseClientRedirect(redirect_to=reverse_lazy("register:success"))

        # ---- case: forms are invalid ---- #

        form_html = render_block_to_string(template_name, "form", context)

        # Make a response with the rendered new list of themes
        htmx_reponse = HttpResponse(form_html)

        print(user_form.errors)
        print(student_form.errors)
        return htmx_reponse


    if request.method == "GET":
        context = get_context(request, action="initial")
        return TemplateResponse(request, template_name, context)
