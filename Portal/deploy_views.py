import hmac
import os
import subprocess
import urllib.request
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

PROJECT_DIR = Path(settings.BASE_DIR)


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
            return JsonResponse({"detail": f"Django command failed: {e}"}, status=500)

        self._reload_webapp()
        return JsonResponse(
            {"detail": "Deployed (no git pull, test)", "output": out.getvalue()[-2000:]}
        )

    def _reload_webapp(self):
        username = os.environ.get("PA_USERNAME")
        api_token = os.environ.get("PA_API_TOKEN")
        domain = f"{username}.pythonanywhere.com"
        url = f"https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/reload/"
        req = urllib.request.Request(
            url, method="POST", headers={"Authorization": f"Token {api_token}"}
        )
        urllib.request.urlopen(req, timeout=30)
