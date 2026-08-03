# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

**RequestEngine** is a full-stack access request workflow portal. Employees submit requests for access to internal applications, which then route through a multi-stage approval chain: Manager → App Owner → Security team. Built with Django REST Framework (backend) + Angular 21 (frontend).

## Running the Project

**Backend** (Django, port 8000):
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Swagger docs at `http://localhost:8000/api/docs/`. User accounts/roles are managed via Django admin only — there is no public registration endpoint.

`python manage.py seed_data` populates the DB with test users (`requester1`/`manager1`/`appowner1`/`security1`, password `pass1234`), sample applications, and requests in various workflow states — useful for manual testing.

Lint: `ruff check .` (ruff is in `requirements.txt`). There are currently no real backend tests (`Portal/tests.py` is boilerplate).

**Frontend** (Angular, port 4200):
```bash
cd frontend
npm install
npm start        # ng serve
npm run build    # production build
npm test         # ng test (vitest) — most feature/shared components have .spec.ts files
```

## Architecture Overview

### Backend (`/Portal/` app)

The core workflow logic lives in two files:
- `Portal/constants.py` — `TRANSITIONS` dict maps `(current_state, action) → (next_state, required_role)`
- `Portal/services.py` — `apply_transition()` executes state changes, writes `WorkflowHistory`, and reassigns `current_owner`

**Workflow states:** `DRAFT → PENDING_MANAGER → PENDING_APP_OWNER → PENDING_SECURITY → APPROVED`  
Side paths: `REJECTED` (terminal from any approval stage), `INFO_REQUESTED` (returns to requester, then resubmit goes back to the stage it was returned from via `returned_from_state` field).

**Models** (`Portal/models.py`):
- `Profile` — OneToOne with Django User; holds `role` (REQUESTER/MANAGER/APP_OWNER/SECURITY) and `manager` FK
- `AccessRequest` — main entity with `current_state`, `current_owner`, `returned_from_state`
- `WorkflowHistory` — immutable audit trail written on every transition

**Ownership assignment** at each stage:
- `PENDING_MANAGER` → requester's `Profile.manager`
- `PENDING_APP_OWNER` → `Application.owner`
- `PENDING_SECURITY` → first user with SECURITY role

**Permissions** (`Portal/permissions.py`) — custom DRF permission classes enforce role-based access per action (e.g. only `current_owner` can approve/reject, only original requester can submit/resubmit).

**API routes** are registered via DRF router in `Portal/urls.py` (`/api/requests/`, `/api/applications/`) and mounted under `/api/` in `RequestEngine/urls.py`. Auth endpoints live at `/api/auth/` (`login`, `refresh`, `logout`, `me`, `change-password`).

Beyond the standard CRUD actions, `AccessRequestViewSet` (`Portal/views.py`) exposes action endpoints: `submit`, `approve`, `reject`, `return_for_info`, `resubmit`, `history`, `pending_approvals` (approver's assigned queue), and `needs_my_response` (requester's items stuck in `INFO_REQUESTED`). Each has its own permission check in `get_permissions()` — don't assume the ViewSet's default `permission_classes` covers a given action.

### Frontend (`/frontend/src/app/`)

Angular 21 standalone components — no NgModules.

```
core/
  auth.ts              # AuthService: login/logout/getCurrentUser, token storage (localStorage)
  auth-interceptor.ts  # Injects Bearer token on every outgoing HTTP request
  auth-guard.ts        # Protects /dashboard route
  request.service.ts   # AccessRequest/Application API calls
  models.ts            # shared TS interfaces mirroring backend serializers
features/
  login/, dashboard/, requests/, request-detail/, create-request/,
  approvals/, applications/, change-password/
shared/
  header/, sidebar/, statistic-card/, loading-spinner/
```

**Route structure:** `/login` (public) → `/dashboard` (guarded). Default redirects to `/login`.

**API base URL** is configured in `frontend/src/environments/environment.ts` (`http://localhost:8000/api`).

**Auth flow:** JWT tokens stored in `localStorage` as `access_token` / `refresh_token`. The interceptor attaches the access token; logout calls `/api/auth/logout/` to blacklist the refresh token.

### Django Settings

- `RequestEngine/settings.py` — CORS allows `localhost:4200`, JWT via SimpleJWT, SQLite for dev
- `DEBUG = True` and `SECRET_KEY` are hardcoded — dev only, not production-ready
- Django admin at `/admin/` with `ProfileInline` attached to User (useful for setting up test users and roles)
