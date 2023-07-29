from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.
class HelloWorld(APIView):
    def get(self, request, format=None):
        return Response({"msg": "howdy mate"})
