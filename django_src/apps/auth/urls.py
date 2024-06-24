from django.urls import path
from .views import change_profile_view, change_password_view

app_name = "customauth"

urlpatterns = [
    path(route="change_profile", view=change_profile_view, name="change_profile"),
    path(route="change_password", view=change_password_view, name="change_password"),
]
