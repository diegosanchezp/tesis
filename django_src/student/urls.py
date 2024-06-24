from django.urls import path
from .track_mentorship_task_view import track_mentorship_task_view, change_task_state
from .profile.view import profile_view
app_name="student"

urlpatterns = [
    path("profile", profile_view, name="profile"),
    path("track_mentorship_task/<int:mentorship_pk>/<int:student_pk>/", track_mentorship_task_view, name="track_mentorship_task"),
    path("change_task_state/<int:task_pk>/", change_task_state, name="change_task_state"),
]
