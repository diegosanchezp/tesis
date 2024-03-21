from django.urls import path

from . import mentor_profile_view, blogs_view
from .mentorship_view import create_mentorship, make_mentorship_request, change_mentorship_status, get_mentorship_tasks
from .mentorship_list_view import list_mentorships

app_name="mentor"
urlpatterns = [
    path('<str:username>/', mentor_profile_view.view, name='profile'),
    path('<str:username>/blogs', blogs_view.view, name='blogs'),
    path('<str:username>/mentorias',list_mentorships, name='mentorias'),
    path("mentorship/create", create_mentorship, name="create_mentorship"),
    path("mentorship/request/<int:mentorship_pk>",make_mentorship_request, name="request_mentorship"),
    path("mentorship/request/tasks/<int:mentorship_pk>",get_mentorship_tasks, name="get_tasks"),
    path("mentorship/request/change_status/<int:mentorship_req_pk>", change_mentorship_status, name="change_mentorship_status"),
]
