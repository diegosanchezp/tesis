from django_src.pro_carreer import student_pro_carreer_view

from django.urls import path

app_name="pro_carreer"
urlpatterns = [
    path("student/", student_pro_carreer_view.view, name="student_carreer_match"),
    path("student/grafo", student_pro_carreer_view.graph_view, name="student_graph_match")
]
