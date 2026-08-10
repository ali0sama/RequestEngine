import os
import sys

import requests

USERNAME = os.environ["PA_USERNAME"]
API_TOKEN = os.environ["PA_API_TOKEN"]
REMOTE_ROOT = f"/home/{USERNAME}/RequestEngine"
API_BASE = f"https://www.pythonanywhere.com/api/v0/user/{USERNAME}/files/path"

EXCLUDE_DIRS = {".git", "node_modules", "venv", "__pycache__", ".github", "staticfiles"}
INCLUDE_TOP = [
    "Portal",
    "RequestEngine",
    "manage.py",
    "requirements.txt",
    "frontend/dist",
]


def upload_file(local_path, remote_path):
    url = f"{API_BASE}{remote_path}"
    with open(local_path, "rb") as f:
        resp = requests.post(
            url,
            headers={"Authorization": f"Token {API_TOKEN}"},
            files={"content": f},
        )
    if resp.status_code not in (200, 201):
        print(f"FAILED {remote_path}: {resp.status_code} {resp.text}")
        return False
    print(f"OK {remote_path}")
    return True


def main():
    ok = True
    for top in INCLUDE_TOP:
        if os.path.isfile(top):
            ok &= upload_file(top, f"{REMOTE_ROOT}/{top}")
            continue
        for root, dirs, files in os.walk(top):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for fname in files:
                local_path = os.path.join(root, fname)
                rel = os.path.relpath(local_path, ".").replace(os.sep, "/")
                ok &= upload_file(local_path, f"{REMOTE_ROOT}/{rel}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
