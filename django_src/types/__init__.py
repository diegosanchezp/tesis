from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails
from django_src.apps.auth.models import User

# Typing pattern recommended by django-stubs:
# https://github.com/typeddjango/django-stubs#how-can-i-create-a-httprequest-thats-guaranteed-to-have-an-authenticated-user
class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
    user: User
