import hmac
import os
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

WSGI_FILE = Path("/var/www/aliosamaportal_pythonanywhere_com_wsgi.py")


@method_decorator(csrf_exempt, name="dispatch")
class DeployWebhookView(View):
    def post(self, request):
        token = request.headers.get("X-Deploy-Token", "")
        expected = os.environ.get("DEPLOY_TOKEN", "")
        if not expected or not hmac.compare_digest(token, expected):
            return JsonResponse({"detail": "Forbidden"}, status=403)

        out = StringIO()
        try:
            call_command("migrate", stdout=out, interactive=False)
            call_command("collectstatic", interactive=False, stdout=out)
        except Exception as e:
            return JsonResponse({"detail": f"call_command failed: {e}"}, status=500)

        WSGI_FILE.touch()
        return JsonResponse({"detail": "Deployed"})
