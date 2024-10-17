from django.http import HttpResponse, HttpResponseForbidden, QueryDict
from django.template.response import TemplateResponse
from django.db.models import Q, Prefetch, Count, Sum
from django.urls import reverse
from render_block import render_block_to_string
from django.views.decorators.http import require_GET

from django_src.apps.register.models import (
    Carreer,
    Student,
    CarrerSpecialization,
    RegisterApprovalStates,
)
from django_src.mentor.utils import loggedin_and_approved
from django_src.utils import get_page_number
from django_src.interests.views import (
    get_interest_theme_page,
    get_interest_theme_page_view,
)
from .students_forms import FilterForm, PaginationForm, ActionForm, Actions


def get_student_queryset():
    students_queryset = Student.objects.approved()
    return students_queryset


def filter_students(
    career_queryset,
    career: Carreer | None = None,
    name_last_name: str | None = None,
    email: str | None = None,
    specialization: CarrerSpecialization | None = None,
    interests=None,
):
    """
    Filters the carreer queryset by
    """

    students_queryset = get_student_queryset()

    if career:
        career_queryset = career_queryset.filter(name=career.name)
    if name_last_name:
        students_queryset = students_queryset.filter(
            Q(user__first_name__icontains=name_last_name)
            | Q(user__last_name__icontains=name_last_name)
        )
    if email:
        students_queryset = students_queryset.filter(user__email=email)
    if interests:
        students_queryset = students_queryset.filter(interests__in=interests)
    if specialization:
        students_queryset = students_queryset.filter(specialization=specialization)


    # distinct remove duplicates
    return {
        "career_queryset": career_queryset.prefetch_related(
            Prefetch("students", queryset=students_queryset.distinct())
        ),
        # Apply the filter to the students queryset so it doesn't returns all of the students
        # useful for agregations
        "students_queryset": students_queryset.filter(carreer__in=career_queryset).distinct('id'),
    }


def paginate_students(page_number: int, carreer: Carreer):
    """
    Limits the student queryset of a career
    """
    page = carreer.paginated_students(page_number)
    return page


@require_GET
@loggedin_and_approved
def students_directory_view(request):
    """ """
    template = "business/directory/students.html"

    if not (request.user.is_business or request.user.is_superuser):
        return HttpResponseForbidden("You are not allowed to view this page")

    carreers = Carreer.objects.order_by("name")

    action_form = ActionForm(data=request.GET)
    filter_form = FilterForm(request.GET)

    context = {
        "carreers": carreers,
        "this_view_url": reverse("business:students_directory"),
        "filter_form": filter_form,
        "Actions": Actions,
        "action_form": action_form,
        "interests_themes": get_interest_theme_page(page_number=1),
        # Is this required ?
        "search_query_params": "",
    }
    action = None
    if action_form.is_valid():
        action = action_form.cleaned_data.get("action")

    # Gets more interests themes for the filter form
    if action == Actions.RENDER_INTERESTS:
        return get_interest_theme_page_view(
            request,
            extra_context={
                "input_name": "interests",
                "small_interest": True,
            },
        )

    if filter_form.is_valid() and action:
        career = filter_form.cleaned_data.get("career")
        name_last_name = filter_form.cleaned_data.get("name_last_name")
        email = filter_form.cleaned_data.get("email")
        interests = filter_form.cleaned_data.get("interests")
        specialization = filter_form.cleaned_data.get("specialization")

        filtered_sets = filter_students(
            career_queryset=carreers,
            career=career,
            name_last_name=name_last_name,
            email=email,
            interests=interests,
            specialization=specialization,
        )
        carreers = filtered_sets["career_queryset"]
        students = filtered_sets["students_queryset"]
        carreers = carreers.annotate(students_num=Count("students"))

        print(filtered_sets["students_queryset"])
        context["carreers"] = carreers

        # Add the number of students as a new column
        context["total_students"] = students.count()
        print(context["total_students"])

        # Convert the form cleaned data to a query string, so it can be used in the pagination links
        form_query_dict = QueryDict(mutable=True)

        # The Carrer name should not be added to the query params string if we are paginating, it is added later in the method career.paginate_search_query_params
        if name_last_name:
            form_query_dict["name_last_name"] = name_last_name
        if email:
            form_query_dict["email"] = email
        if interests and interests.exists():
            form_query_dict.setlist(
                "interests", interests.values_list("name", flat=True)
            )

        # Convert the query dict to a query string
        form_query_string = form_query_dict.urlencode()
        context["form_query_string"] = form_query_string

        if action == Actions.FILTER_STUDENTS:
            if request.htmx:
                html = render_block_to_string(
                    block_name="career_students",
                    template_name="business/directory/students.html",
                    context=context,
                )
                return HttpResponse(html)
    else:

        # We add the pretech here, because the filter_students function adds it's own prefetch, if the conditional above is true
        carreers = carreers.prefetch_related(
            Prefetch("students", queryset=get_student_queryset().distinct())
        )

        # Add the number of students as a new column
        carreers = carreers.annotate(students_num=Count("students"))
        context.update(carreers=carreers)

    # Pagination and filtering is suported for both normal and htmx requests
    if action == Actions.FILTER_PAGINATE_STUDENTS:
        pagination_form = PaginationForm(data=request.GET)
        if pagination_form.is_valid():

            career: Carreer = pagination_form.cleaned_data["carreer"]
            # Get from the carreers queryset since it has the students are already filtered in the prefetch
            career = carreers.get(name=career.name)

            page_number = get_page_number(request)
            page = paginate_students(page_number=page_number, carreer=career)

            # Add the form query string to the pagination query string
            paginate_search_query_params = career.paginate_search_query_params
            form_query_string = context.get("form_query_string")
            if form_query_string:
                paginate_search_query_params += f"&{form_query_string}"

            if not request.htmx:
                context.update(
                    {
                        "page_carreer": career,
                        "page_students": page,
                        "search_query_params": paginate_search_query_params,
                    }
                )

            if request.htmx:
                context.update(
                    {
                        "students": page,
                        "carreer": career,
                        "search_query_params": paginate_search_query_params,
                    }
                )

                return TemplateResponse(
                    request,
                    template="business/directory/students_row_page.html",
                    context=context,
                )

    return TemplateResponse(request, template, context)
