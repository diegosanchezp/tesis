from django.urls import path
from .track_mentorship_task_view import track_mentorship_task_view, change_task_state
from .mentorships.my_mentorships_view import student_mentorships_view
from .profile.view import profile_view
from .jobs.jobs_view import jobs_view
app_name="student"

urlpatterns = [
    path("profile", profile_view, name="profile"),
    path("job_offers", jobs_view, name="jobs_offers"),
    path("my_mentorships", student_mentorships_view ,name="my_mentorships"),
    path("track_mentorship_task/<int:mentorship_pk>/<int:student_pk>/", track_mentorship_task_view, name="track_mentorship_task"),
    path("change_task_state/<int:task_pk>/", change_task_state, name="change_task_state"),
]
