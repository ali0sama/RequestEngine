import hmac
import os

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class DeployWebhookView(View):
    def post(self, request):
        token = request.headers.get("X-Deploy-Token", "")
        expected = os.environ.get("DEPLOY_TOKEN", "")
        if not expected or not hmac.compare_digest(token, expected):
            return JsonResponse({"detail": "Forbidden"}, status=403)
        return JsonResponse({"detail": "Minimal test OK"})
