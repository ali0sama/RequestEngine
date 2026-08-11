# Access Request Workflow Portal

A centralized, auditable web application for employees to request access to internal applications, replacing ad-hoc email requests with a structured, multi-stage approval workflow.


## Table of Contents

- [Overview](#overview)
- [How the Workflow Works](#how-the-workflow-works)
- [Roles](#roles)
- [Features](#features)
- [Pages](#pages)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running Both Together](#running-both-together)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)

---

## Overview

Every access request moves through the same approval chain:

**Requester → Line Manager → Application Owner → Security Team → Completed**

Each step is validated, logged, and restricted to the right person — with a permanent, timestamped history of every decision made along the way.

## How the Workflow Works

1. An employee submits a request for a specific internal application with a business justification.
2. Their line manager reviews it — approve, reject, or return it for more information.
3. If approved, it moves to the owner of the requested application.
4. If approved again, it moves to the Security Team for a final review.
5. Once Security approves, the request is complete.

At any stage, an approver can **return a request for more information** instead of approving or rejecting. This sends it back to the requester; once they respond and resubmit, the request resumes at the exact stage it was returned from, rather than restarting the chain.

## Roles

| Role | Capabilities |
|---|---|
| **Requester** | Submit requests, track status and history, respond to information requests |
| **Line Manager** | Approve/reject/return requests from their direct reports |
| **Application Owner** | Approve/reject/return requests for applications they own |
| **Security Team** | Final approval/rejection before a request is completed |

A user can hold multiple roles — e.g. a manager may also submit their own requests as a requester.

## Features

- **Full audit trail** — every workflow action is permanently recorded with actor, timestamp, and comments
- **Role-based authorization** — enforced at three layers: authentication, object-level ownership, and workflow-stage role checks
- **Return-and-resume** — requests returned for clarification resume at the correct stage on resubmission, never restarting
- **JWT authentication** — login, refresh, logout (with token blacklisting), and password change
- **Interactive API docs** — full Swagger UI generated from the codebase

## Pages

| Page | Description |
|---|---|
| Dashboard | Summary of the user's requests and pending approvals |
| Create Request | Submit a new access request |
| My Requests | All requests submitted by the current user |
| Request Details | Full detail and timeline for a single request |
| Pending Approvals | Requests awaiting the current user's decision |
| Approval Details | Request detail with approve/reject/return actions |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django, Django REST Framework |
| Auth | JWT (`djangorestframework-simplejwt`) |
| API Docs | `drf-spectacular` (Swagger UI) |
| Frontend | Angular (standalone components) |
| Database | SQLite (development) |

## Project Structure

```
RequestEngine/
├── RequestEngine/        # Django project config
├── Portal/                # Django app — models, serializers, views, workflow engine
│   ├── models.py
│   ├── constants.py       # workflow transition table
│   ├── services.py        # workflow engine
│   ├── serializers.py
│   ├── permissions.py
│   ├── views.py
│   └── urls.py
├── frontend/               # Angular application
│   └── src/app/
│       ├── core/            # auth service, guard, interceptor
│       ├── features/        # one folder per page
│       └── shared/          # reusable components
├── manage.py
└── requirements.txt
```

## Getting Started

### Backend Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Backend runs at `http://127.0.0.1:8000/`.

- Admin panel: `/admin/`
- Swagger docs: `/api/docs/`

> User accounts and roles (`REQUESTER`, `MANAGER`, `APP_OWNER`, `SECURITY`) are managed exclusively through Django admin — there is no public registration endpoint by design.

### Frontend Setup

```bash
cd frontend
npm install
ng serve
```

Frontend runs at `http://localhost:4200/`.

The backend API URL is configured in `frontend/src/environments/environment.ts`.

### Running Both Together

Both servers must run simultaneously in separate terminals:

```bash
# Terminal 1
venv\Scripts\activate
python manage.py runserver

# Terminal 2
cd frontend
ng serve
```

Then visit `http://localhost:4200/`. CORS is configured on the backend to accept requests from the Angular dev server.

## Architecture

### Workflow Engine

The approval logic is centralized in `Portal/services.py` (`apply_transition`), driven by a static transition table in `Portal/constants.py`. Every transition validates the current state, the actor's role, and their ownership of the request, then atomically updates the request and writes an immutable `WorkflowHistory` entry.

### Authorization — three layers

1. **Authentication** (JWT) — resolves the request to a real user
2. **Object-level permissions** — is this user allowed to touch this specific request
3. **Workflow engine role check** — does the actor's role match what's required at this exact stage

### Key Models

- `Profile` — extends Django's `User` with `role` and `manager`
- `Application` — an internal system with an assigned owner
- `AccessRequest` — the core entity; tracks `current_state` and `current_owner`
- `WorkflowHistory` — append-only audit log of every transition

## API Documentation

Full interactive documentation with request/response schemas is available via Swagger at `/api/docs/` once the backend is running.

| Group | Endpoints |
|---|---|
| Auth | `/api/auth/login/`, `/refresh/`, `/logout/`, `/me/`, `/change-password/` |
| Applications | `/api/applications/` |
| Requests | `/api/requests/` — create, list, detail, submit, approve, reject, return-for-info, resubmit, pending-approvals, history |

## Deployed Version

URL: https://aliosamaportal.pythonanywhere.com/

Test Users-> 

             (REQUESTER)    username: marcus.reyes
                            password: pass1234
                            
             (LINE_MANAGER) username: daniel.foster
                            password: pass1234
                            
             (APP_OWNER)    username: lucas.moreau
                            password: pass1234

             (SECURITY)     username: sophia.becker
                            password: pass1234
