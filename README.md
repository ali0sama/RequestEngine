# Access Request Workflow API

A Django REST Framework backend that powers an Access Request Workflow Portal. The system allows employees to submit access requests for internal applications and routes them through a configurable multi-stage approval workflow.

The API enforces business rules, validates workflow transitions, records approval history, and provides complete auditability throughout the request lifecycle.

---

## Features

### Request Management

- Create access requests
- Retrieve submitted requests
- View request details
- Track current request status
- View workflow history

### Workflow Engine

- Multi-stage approval workflow
- Configurable workflow transitions
- Validation of allowed state changes
- Automatic routing to the next approver
- Prevention of invalid transitions

### Approval Process

Approvers can:

- Approve requests
- Reject requests
- Request additional information
- Add approval comments

### Audit & Tracking

- Workflow history
- Audit logging
- Current request owner tracking
- Action timestamps

### API

- RESTful endpoints
- JSON responses
- Proper HTTP status codes
- Input validation
- Centralized exception handling

---

## Tech Stack

- Python
- Django
- Django REST Framework
- SQLite / PostgreSQL
- Ruff
- Git

---

## Project Structure

```
backend/
│
├── access_request/
│   ├── migrations/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   ├── exceptions.py
│   ├── constants.py
│   └── permissions.py
│
├── config/
│
├── manage.py
│
└── requirements.txt
```

---

## Workflow

```
Requester
    │
    ▼
Line Manager
    │
    ▼
Application Owner
    │
    ▼
Security Team
    │
    ▼
Completed
```

Possible actions during the workflow:

- Approve
- Reject
- Request More Information
- Resubmit

---

## Installation

### Clone the repository

```bash
git clone https://github.com/ali0sama/RequestEngine.git

cd RequestEngine
```

### Create a virtual environment

```bash
python -m venv venv
```

### Activate the environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Apply migrations

```bash
python manage.py migrate
```

### Run the development server

```bash
python manage.py runserver
```

---

## API Overview

The API provides endpoints for:

- Managing access requests
- Processing workflow actions
- Retrieving workflow history
- Viewing pending approvals
- Managing request states

---

## Business Rules

- Only valid workflow transitions are allowed.
- Every action is recorded in the workflow history.
- Invalid transitions raise exceptions.
- Each request always has a current owner.
- Requests move through predefined approval stages.

---

## Error Handling

The project includes centralized exception handling for:

- Invalid workflow transitions
- Unauthorized actions
- Validation errors
- Resource not found
- Internal server errors

---

## Future Improvements

- JWT Authentication
- Role-based permissions
- Email notifications
- Swagger / OpenAPI documentation
- Docker support
- Unit and integration testing
- CI/CD pipeline

---

## Author

**Ali Osama**

GitHub: https://github.com/ali0sama

LinkedIn: https://www.linkedin.com/in/ali-osama-7673b2352/

---

## License

This project was developed for educational purposes as part of a backend onboarding project.
