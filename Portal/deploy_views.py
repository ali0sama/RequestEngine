import hmac
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from django.conf import settings
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

        python_bin = os.environ.get("VENV_PYTHON", sys.executable)

        steps = [
            ["git", "pull", "origin", "main"],
            [python_bin, "-m", "pip", "install", "-r", "requirements.txt"],
            [python_bin, "manage.py", "migrate"],
            [python_bin, "manage.py", "collectstatic", "--noinput"],
        ]

        results = []
        for step in steps:
            try:
                result = subprocess.run(
                    step, cwd=PROJECT_DIR, capture_output=True, text=True, timeout=20
                )
            except subprocess.TimeoutExpired:
                results.append({"cmd": " ".join(step), "returncode": "TIMEOUT"})
                return JsonResponse(
                    {"detail": "Deploy step timed out", "steps": results}, status=500
                )

            results.append({"cmd": " ".join(step), "returncode": result.returncode})
            if result.returncode != 0:
                return JsonResponse(
                    {
                        "detail": "Deploy step failed",
                        "steps": results,
                        "stderr": result.stderr[-2000:],
                    },
                    status=500,
                )

        self._reload_webapp()
        return JsonResponse({"detail": "Deployed", "steps": results})

    def _reload_webapp(self):
        username = os.environ.get("PA_USERNAME")
        api_token = os.environ.get("PA_API_TOKEN")
        domain = f"{username}.pythonanywhere.com"
        url = f"https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{domain}/reload/"
        req = urllib.request.Request(
            url, method="POST", headers={"Authorization": f"Token {api_token}"}
        )
        urllib.request.urlopen(req, timeout=30)
