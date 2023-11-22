from django.urls import path
from .views import MainView, SelectCarreraView, SelectCarrerSpecialization, SelecThemeView
from .complete_profile_view import complete_profile_view
from .views import register_sucess_view
app_name="register"

urlpatterns = [
    path("select_carrera/", SelectCarreraView.as_view(), name="select_carrera"),
    path("select_carreer_specialization/<str:name>", SelectCarrerSpecialization.as_view(), name="select_specialization"),
    path("select_themes/<str:name>", SelecThemeView.as_view(), name="select_themes"),
    path("complete_profile", complete_profile_view, name="complete_profile"),
    path("success", register_sucess_view, name="success"),
    path("", MainView.as_view(), name="index"),
]
