from django.urls import path

from .directory.students_view import students_directory_view

app_name = "business"
urlpatterns = [
    path(
        route="directory/students/",
        view=students_directory_view,
        name="students_directory",
    ),
]
