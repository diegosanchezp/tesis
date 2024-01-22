import functools

from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponseForbidden
from django.utils.translation import gettext_lazy as _

from django_src.apps.register.models import (
    RegisterApprovalStates, Student, InterestTheme, CarrerSpecialization,
    RegisterApprovals,
)

from .models import ProfessionalCarreer
def get_student(request):
    return Student.objects.get(user=request.user)


# use this function on def view()
def get_queryset(request):
    """
    Get the queryset of professional carreers that match the student's interests
    or specialization
    """

    student = get_student(request)

    # Determine the content type of the theme spec

    # Case when the student has interests
    if student.interests.count() > 0:
        themespec_content_type = ContentType.objects.get_for_model(InterestTheme)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = ProfessionalCarreer.objects.filter(
            weighted_themespecs__content_type=themespec_content_type,
            weighted_themespecs__object_id__in=student.interests.all(),
        )
    # Case when the student has a specialization
    elif student.specialization:
        themespec_content_type = ContentType.objects.get_for_model(CarrerSpecialization)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = ProfessionalCarreer.objects.filter(
            weighted_themespecs__content_type=themespec_content_type,
            weighted_themespecs__object_id=student.specialization.id,
        )
    # Case when the student has no interests nor specialization
    else:
        student_match_procarreers = ProfessionalCarreer.objects.none()
        # Should i raise an http404 here?


    # Get all professional carreers that match with the student interests
    # distinct() is used to avoid duplicates because of the order_by

    return student_match_procarreers.order_by("-weighted_themespecs__weight").distinct()

def student_is_approved(func):
    """
    Checks that the student is approved
    """

    @functools.wraps(func)
    def inner(request, *args, **kwargs):
        try:
            student_type = ContentType.objects.get_for_model(Student)
            try:
                approval = RegisterApprovals.objects.get(user=request.user,user_type=student_type)

                if approval.state == RegisterApprovalStates.APPROVED:
                    return func(request, *args, **kwargs)
                else:
                    return HttpResponseForbidden(_("Tu solicitud de registro no ha sido aprobada"))
            except RegisterApprovals.DoesNotExist:
                return HttpResponseForbidden(_("No existe registro de aprobación"))
        except Student.DoesNotExist:
            return HttpResponseForbidden(_("No te has registrado como estudiante, para ver esta página"))
    return inner


@require_GET
@login_required(login_url="/")
@student_is_approved
def view(request):
    """
    The first view that the student sees when he logs in for the first time
    """
    template_name = "pro_carreer/student_match.html"
    context = {}

    if not student_is_approved(request):
        # Todo a template for this, that says you are not approved yet
        return HttpResponseForbidden("You are not approved yet")

    pro_careers: QuerySet[ProfessionalCarreer] = get_queryset(request)
    graph_data = get_graph_data()

    context["pro_careers"] = pro_careers
    context["graph_data"] = graph_data

    # We are visiting the page for the first time
    # if request.method == "GET" and not request.htmx:

    return TemplateResponse(request, template_name, context)

def get_graph_data():
    """
    Get the data for the graph
    """

    careers_spec = CarrerSpecialization.objects.select_related("career__faculty").prefetch_related("pro_carreers_match")

    # History
    pro_careers_added = []
    faculties_added = []
    careers_added = []
    careers_spec_added = []
    edges_added = []

    # cytoscape elements
    elements_nodes = []
    elements_edges = []

    # If i loop the careers queryset, the faculty should be cached
    for career_spec in careers_spec:

        # ---- Add nodes ----

        # Career specialization node
        if career_spec.name not in careers_spec_added:
            elements_nodes.append({
                "data": {
                    "id": career_spec.name,
                    "name": career_spec.name,
                    "description": f"Especialización",
                    "NodeType": "CareerSpec",
                },
            })
            careers_spec_added.append(career_spec.name)

        # Academic Career node
        if career_spec.career.name not in careers_added:
            elements_nodes.append({
                "data": {
                    "id": career_spec.career.name,
                    "name": career_spec.career.name,
                    "description": f"Carrera Académica",
                    "NodeType": "AcademicCareer",
                },
            })
            careers_added.append(career_spec.career.name)

        # faculty nodes
        if career_spec.career.faculty.name not in faculties_added:
            elements_nodes.append({
                "data": {
                    "id": career_spec.career.faculty.name,
                    "name": career_spec.career.faculty.name,
                    "description": "Facultad",
                    "NodeType": "Faculty",
                },
            })
            faculties_added.append(career_spec.career.faculty.name)

        # ---- Add edges ----

        # faculty -> career
        edge_id = f"{career_spec.career.faculty.name}-{career_spec.career.name}"

        if edge_id not in edges_added:
            elements_edges.append({
                "data": {
                    "id": edge_id,
                    "source": career_spec.career.faculty.name,
                    "target": career_spec.career.name
                }
            })
            edges_added.append(edge_id)

        # career -> career specialization
        edge_id = f"{career_spec.career.name}-{career_spec.name}"
        if edge_id not in edges_added:
            elements_edges.append({
                "data": {
                    "id": edge_id,
                    "source": career_spec.career.name,
                    "target": career_spec.name
                }
            })
            edges_added.append(edge_id)

        pro_carreers_matches = career_spec.pro_carreers_match.all()

        # career specialization -> professional career
        for pro_carreer_match in pro_carreers_matches:

            pro_career = pro_carreer_match.pro_career

            # Career spec are the leaf nodes
            if pro_career.title not in pro_careers_added:

                imgURL = pro_career.image.get_rendition("original").url if pro_career.image else ""
                elements_nodes.append({
                    "data": {
                        "id": pro_career.title,
                        "name": pro_career.title,
                        "description": pro_career.short_description,
                        "NodeType": "ProfessionalCareer",
                        "imgURL": imgURL,
                    },
                })

                pro_careers_added.append(pro_career.title)

            # career specialization -> professional career

            edge_id = f"{career_spec.name}-{pro_career.title}"

            if edge_id not in edges_added:
                elements_edges.append({
                    "data": {
                        "id": edge_id,
                        "source": career_spec.name,
                        "target": pro_career.title
                    }
                })
                edges_added.append(edge_id)
            # ---- End add edges ----

    # Transform to dict
    elements = {
        "nodes": elements_nodes,
        "edges": elements_edges,
    }

    return elements

@require_GET
@login_required(login_url="/")
@student_is_approved
def graph_view(request):

    template_name = "pro_carreer/graph.html"
    context = {}

    graph_data = get_graph_data()
    context["graph_data"] = graph_data

    return TemplateResponse(request, template_name, context)
