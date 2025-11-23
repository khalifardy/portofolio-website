from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from .views import check_telescope_status


class TelescopeStatusAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        status = check_telescope_status()
        return Response(status)