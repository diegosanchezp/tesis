from django.urls import path
from .views import root_view

app_name = "egresados_update"

urlpatterns = [
    path(
        route="",
        view=root_view,
        name="root",
    ),
]
