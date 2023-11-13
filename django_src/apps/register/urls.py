from django.urls import path
from .views import MainView, SelectCarreraView, SelectCarrerSpecialization, SelecThemeView

app_name="register"

urlpatterns = [
    path("select_carrera/", SelectCarreraView.as_view(), name="select_carrera"),
    path("select_carreer_specialization/<str:name>", SelectCarrerSpecialization.as_view(), name="select_specialization"),
    path("select_themes/<str:name>", SelecThemeView.as_view(), name="select_themes"),
    path("", MainView.as_view(), name="index"),

]
