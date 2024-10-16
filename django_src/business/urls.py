from django.urls import path

from .directory.students_view import students_directory_view
from .directory.mentors.mentors_view import mentors_directory_view
from .landing.view import landing_view
from .edit_profile.view import business_edit_profile_view

app_name = "business"
urlpatterns = [
    path(
        route="",
        view=landing_view,
        name="landing",
    ),
    path(
        route="edit_profile",
        view=business_edit_profile_view,
        name="edit_profile",
    ),
    path(
        route="directory/students/",
        view=students_directory_view,
        name="students_directory",
    ),
    path(
        route="directory/mentors/",
        view=mentors_directory_view,
        name="mentors_directory",
    ),
]
