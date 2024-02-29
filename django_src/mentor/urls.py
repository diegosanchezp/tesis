from django.urls import path

from . import mentor_profile_view, blogs_view

app_name="mentor"
urlpatterns = [
    path('<str:username>/', mentor_profile_view.view, name='profile'),
    # Todo change view fn
    path('<str:username>/blogs', blogs_view.view, name='blogs'),
    path('<str:username>/mentorias', mentor_profile_view.view, name='mentorias'),
]
