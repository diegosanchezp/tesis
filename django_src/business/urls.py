from django.urls import path

from .directory.students_view import students_directory_view
from .landing.view import landing_view

app_name = "business"
urlpatterns = [
    path(
        route="",
        view=landing_view,
        name="landing",
    ),
    path(
        route="directory/students/",
        view=students_directory_view,
        name="students_directory",
    ),
]
