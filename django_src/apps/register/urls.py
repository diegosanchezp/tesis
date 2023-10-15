from django.urls import path
from .views import MainView

app_name="register"

urlpatterns = [
    path("", MainView.as_view(), name="index")
]
