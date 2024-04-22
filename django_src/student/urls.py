from django.urls import path
from .track_mentorship_task_view import track_mentorship_task_view

app_name="mentor"

urlpatterns = [
    path("track_mentorship_task/<int:mentorship_pk>/", track_mentorship_task_view, name="track_mentorship_task"),
]
