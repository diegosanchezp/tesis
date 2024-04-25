from django.urls import path

from . import mentor_profile_view, blogs_view
from .mentorship_view import create_mentorship, make_mentorship_request, change_mentorship_status, get_mentorship_tasks
from .mentorship_detail_view import mentorship_detail_view, student_info_view
from .mentorship_list_view import list_mentorships, my_mentorships
from .edit_mentorship_view import edit_mentorship_view, delete_task, delete_mentorship

app_name="mentor"
urlpatterns = [
    path("my_mentorships/", my_mentorships, name="my_mentorships"),
    path('<str:username>/', mentor_profile_view.view, name='profile'),
    path('<str:username>/blogs/', blogs_view.view, name='blogs'),
    path('<str:username>/mentorias/',list_mentorships, name='mentorias'),
    path("mentorship/<int:mentorship_pk>", mentorship_detail_view, name="mentorship_detail"),
    path("mentorship/create", create_mentorship, name="create_mentorship"),
    path("mentorship/edit/<int:mentorship_pk>", edit_mentorship_view, name="edit_mentorship"),
    path("mentorship/delete/<int:mentorship_pk>", delete_mentorship, name="delete_mentorship"),
    path("mentorship/delete_task/<int:task_pk>", delete_task, name="delete_task"),
    path("mentorship/student_info/<int:mentorship_request_pk>", student_info_view, name="student_info_modal"),
    path("mentorship/request/<int:mentorship_pk>",make_mentorship_request, name="request_mentorship"),
    path("mentorship/request/tasks/<int:mentorship_pk>",get_mentorship_tasks, name="get_tasks"),
    path("mentorship/request/change_status/<int:mentorship_req_pk>", change_mentorship_status, name="change_mentorship_status"),
]
