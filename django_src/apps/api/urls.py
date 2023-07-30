from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework import routers

from django.urls import path, include

from rest_framework.routers import DefaultRouter, SimpleRouter
from .views import HelloWorld
from django.conf import settings

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

urlpatterns = [
    path("hello/", HelloWorld.as_view(), name="greet"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path(
        "docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Optional UI:
    path(
        "docs/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns += router.urls
