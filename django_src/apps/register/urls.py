from django.urls import path
from .views import MainView, SelectCarreraView

app_name="register"

urlpatterns = [
    path("select_carrera/", SelectCarreraView.as_view(), name="select_carrera"),
    path("", MainView.as_view(), name="index"),

]