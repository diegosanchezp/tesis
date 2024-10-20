from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Count, Q, FloatField, Value
from django.core.paginator import Paginator
from django.urls.base import reverse_lazy
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from django_htmx.http import trigger_client_event
from render_block import render_block_to_string

from .models import ProfessionalCarreer, ProCarreerExperience
from .forms import ProCareerExpForm
from django_src.mentor.utils import loggedin_and_approved
from django_src.apps.register.models import Mentor
from django_src.utils.webui import renderMessagesAsToasts

def get_distribution(pro_career: ProfessionalCarreer):
    """
    Calculate the distribution of ratings for a pro_career page.
    """

    experiences = pro_career.career_experiences.all()

    total_experiences = experiences.count() or 1

    distribution = experiences.aggregate(
        one_star=Count("pk", filter=Q(rating=1)) / Value(total_experiences, output_field=FloatField()) * 100,
        two_star=Count("pk", filter=Q(rating=2)) / Value(total_experiences, output_field=FloatField()) * 100,
        three_star=Count("pk", filter=Q(rating=3)) / Value(total_experiences, output_field=FloatField()) * 100,
        four_star=Count("pk", filter=Q(rating=4)) / Value(total_experiences, output_field=FloatField()) * 100,
        five_star=Count("pk", filter=Q(rating=5)) / Value(total_experiences, output_field=FloatField()) * 100,
    )

    return distribution

def render_distribution(request, pro_career: ProfessionalCarreer):
    template_name = "pro_carreer/experience_detail.html"
    context = {
        "distribution": get_distribution(pro_career=pro_career),
    }

    html = render_block_to_string(template_name, "rating_distribution", context)

    # Make a response with the rendered new list of themes
    htmx_reponse = HttpResponse(html)

    return htmx_reponse

def get_page_number(request):
    page_number: str | int | None = request.GET.get("page") or request.POST.get("page")

    if page_number is None:
        page_number = 1
    elif isinstance(page_number, str):
        page_number = int(page_number)

    return page_number

def paginate_queryset(request, queryset: QuerySet[ProCarreerExperience]):

    paginator = Paginator(object_list=queryset, per_page=12)  # Change Show 12 experiences.
    page_number = get_page_number(request)
    paginated_experencies = paginator.get_page(page_number)

    return {
        "experiences": paginated_experencies,
        "page_number": page_number,
    }

def get_experiences(request, page):
    experiences = page.career_experiences.all()

    # If the view is being visited by a mentor user
    mentor_experience = None
    mentor_exp_exists = False
    is_mentor = request.user.is_mentor

    if is_mentor:
        mentor_experience = experiences.filter(mentor__user=request.user)
        mentor_exp_exists = mentor_experience.exists()

        # Exclude the mentor from the experiences

        if mentor_exp_exists:
            experiences = experiences.exclude(mentor__user=request.user)

    context = {
        "experiences": experiences.order_by("-rating"),
        "is_mentor": is_mentor,
    }
    if mentor_exp_exists:
        context["mentor_experience"] = mentor_experience.first()
    else:
        context["mentor_experience"] = None

    return context

def render_exp_form(request, pk_pro_career_exp: int):
    """
    Renders the edit form for a professional career experience
    """

    pro_career_exp = get_object_or_404(klass=ProCarreerExperience, pk=pk_pro_career_exp)

    form = ProCareerExpForm(instance=pro_career_exp)

    context = {
        "form": form,
        "mentor": pro_career_exp.mentor,
        "mentor_experience": pro_career_exp,
        "state": "editing",
    }

    return TemplateResponse(request, "pro_carreer/mentor_exp.html", context)

def render_empty_exp_form(request):
    mentor = get_object_or_404(klass=Mentor, user=request.user)

    form = ProCareerExpForm()

    context = {
        "form": form,
        "state": "adding",
        "rating_range_unselected": range(1, 6),
        "mentor": mentor,
    }

    return TemplateResponse(request, "pro_carreer/mentor_exp.html", context)

def trigger_render_distribution(htmx_reponse):
    trigger_client_event(
        response=htmx_reponse,
        name="render_distribution",
        params={}
    )

def add_exp(request, pro_carreer: ProfessionalCarreer):

    form = ProCareerExpForm(data=request.POST)
    mentor = get_object_or_404(klass=Mentor, user=request.user)

    context = {
        "mentor": mentor,
    }

    if form.is_valid():
        # Save to db
        mentor_experience = form.save(commit=False)
        mentor_experience.mentor = mentor
        mentor_experience.pro_carreer = pro_carreer
        mentor_experience.save()

        context.update({
            "mentor_experience": mentor_experience,
            "state": "viewing",
        })
    else:
        context["state"] = "adding"
        context["form"] = form


    return TemplateResponse(request, "pro_carreer/mentor_exp.html", context)

def edit_exp(request, pk_pro_career_exp: int):
    """
    Edit a professional career experience
    """

    pro_career_exp = get_object_or_404(klass=ProCarreerExperience, pk=pk_pro_career_exp)

    form = ProCareerExpForm(data=request.POST, instance=pro_career_exp)

    if not form.is_valid():
        context = {
            "form": form,
            "mentor": pro_career_exp.mentor,
            "mentor_experience": pro_career_exp,
            "state": "editing",
        }
        return TemplateResponse(request, "pro_carreer/mentor_exp.html", context)

    # Save to db
    form.save()
    messages.success(request, _("Edición exitosa"))

    context = {
        "mentor_experience": pro_career_exp,
        "mentor": pro_career_exp.mentor,
        "state": "viewing",
    }

    response = TemplateResponse(request, "pro_carreer/mentor_exp.html", context)

    trigger_render_distribution(response)
    renderMessagesAsToasts(request, response)

    return response

def delete_exp(request, pk_pro_career_exp: int):
    """
    Delete a professional career experience
    """

    pro_career_exp = get_object_or_404(klass=ProCarreerExperience, pk=pk_pro_career_exp)

    pro_career_exp.delete()
    messages.success(request,_("Experiencia borrada"))
    response = HttpResponse(status=200)
    renderMessagesAsToasts(request,response)

    return response

@loggedin_and_approved
def view(request, page: ProfessionalCarreer, page_ctx):
    """
    Experience view for a professional career
    """

    template_name = "pro_carreer/experience_detail.html"

    # Todo prefetch_related career_experiences and paginate

    href = None
    if request.user.is_student:
        href = reverse_lazy("pro_carreer:student_carreer_match")
    else:
        href = page.get_parent().get_url()
    context = {
        "page": page, # Wagtail page object
        "distribution": get_distribution(page),
        "state": "viewing",
        "breadcrumbs": [
            {"name": "Carreras profesionales", "href": href},
            {"name": page.title },
        ],
    } | page_ctx

    context.update(get_experiences(request, page))
    context.update(paginate_queryset(request, context["experiences"]))

    return TemplateResponse(request, template_name, context)
