from pathlib import Path

from django.conf import settings
from django.views.static import serve as static_serve

FRONTEND_DIR = Path(settings.BASE_DIR) / "frontend" / "dist" / "frontend" / "browser"


def serve_frontend(request, path=""):
    full_path = FRONTEND_DIR / path
    if path and full_path.is_file():
        return static_serve(request, path, document_root=str(FRONTEND_DIR))
    return static_serve(request, "index.html", document_root=str(FRONTEND_DIR))
