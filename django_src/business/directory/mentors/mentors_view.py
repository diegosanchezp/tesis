from django.template.response import TemplateResponse

mentors_directory_template = ""
def mentors_directory_view():
    context = {}
    return TemplateResponse(mentors_directory_view,context)
