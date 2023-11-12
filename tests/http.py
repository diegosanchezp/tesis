# Core python libs
from pathlib import Path
import unittest

from django.http.request import QueryDict, HttpRequest

from django.urls.base import reverse_lazy

from shscripts.backup import (
    setup_django,
)

class TestHTTP(unittest.TestCase):

    def setUp(self):
        self.BASE_DIR = Path(__file__).resolve().parent.parent  # Parent Directory of this file
        setup_django(self.BASE_DIR)

    # python -m unittest tests.http.TestHTTP.test_queryDict
    def test_queryDict(self):
        """
        # https://docs.djangoproject.com/en/4.2/ref/request-response/#django.http.QueryDict
        """

        themes = ["Matematicas", "CSS"]

        query_string = "theme=Matematicas&theme=CSS"
        query_dict = QueryDict(query_string=query_string)

        self.assertEqual(query_dict.getlist("theme"), themes)

        # Build a query string from a query dict
        q_fresh = QueryDict(mutable=True)

        q_fresh.setlist("theme", themes)

        self.assertEqual(
            q_fresh.urlencode(),
            query_string
        )

    # python -m unittest tests.http.TestHTTP.testHTTPRequest
    def testHTTPRequest(self):
        url = reverse_lazy("register:select_themes", kwargs={"name":"Computación"})
        request = HttpRequest().path = url
        request.data
        print(request.build_absolute_uri())


