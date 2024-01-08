from django.db.models.query import QuerySet
from django.template.response import TemplateResponse
from django.contrib.contenttypes.models import ContentType

from django_src.apps.register.models import Student, InterestTheme, CarrerSpecialization
from .models import ProfessionalCarreer

def get_student(request):
    return Student.objects.get(user=request.user)

# TODO: use this function on def view()
def get_queryset(request):
    """
    Get the queryset of professional carreers that match the student's interests
    or specialization
    """

    student = get_student(request)

    # Determine the content type of the theme spec
    if student.interests.count() > 0:
        themespec_content_type = ContentType.objects.get_for_model(InterestTheme)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = ProfessionalCarreer.objects.filter(
            weighted_themespecs__content_type=themespec_content_type,
            weighted_themespecs__object_id__in=student.interests.all(),
        )

    elif student.specialization:
        themespec_content_type = ContentType.objects.get_for_model(CarrerSpecialization)

        student_match_procarreers: QuerySet[ProfessionalCarreer] = ProfessionalCarreer.objects.filter(
            weighted_themespecs__content_type=themespec_content_type,
            weighted_themespecs__object_id=student.specialization.id,
        )
    else:
        student_match_procarreers = ProfessionalCarreer.objects.none()
        # Should i raise an http404 here?


    # Get all professional carreers that match with the student interests
    # distinct() is used to avoid duplicates because of the order_by

    return student_match_procarreers.order_by("-weighted_themespecs__weight").distinct()

def view(request):
    """
    The first view that the student sees when he logs in for the first time
    """

    template_name = "pro_carreer/student_match.html"
    context = {}

    # We are visiting the page for the first time, or asking for a filtered page
    if request.method == "GET" and not request.htmx:
        return TemplateResponse(request, template_name, context)
