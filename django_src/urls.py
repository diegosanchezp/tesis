from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView, RedirectView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token
from django_src.apps.main.views import PrivateMediaView
# Wagtail
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Wagtail
    path('cms/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    # End wagtail

    #path('i18n/', include('django.conf.urls.i18n')),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path('accounts/', include('allauth.urls')),

    # Landing page Wagtail
    # Placing at the end ensures that it doesn’t override more specific URL patterns.
    path('', include(wagtail_urls)),

]

if settings.DEBUG:

    # Simulate NGINX authenticated request
    serve_login = login_required(serve)

    MEDIA_URL = settings.MEDIA_URL.lstrip("/")
    urlpatterns += [
        # First path below is similar to
        # + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        path(f"{MEDIA_URL}<path:path>/", serve, {'document_root': settings.MEDIA_ROOT,  'show_indexes':True},),
        path("private_media/<path:path>/", serve_login, {'document_root': settings.PRIVATE_MEDIA_ROOT,}),
    ]
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
else:
    urlpatterns += [
        # NGINX authenticated request
        path("private_media/<path:file_path>", PrivateMediaView.as_view())
    ]

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("django_src.apps.api.urls")),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
