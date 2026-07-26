# Access Request Workflow Portal

A full-stack workflow management application that allows employees to request access to internal systems through a structured approval process instead of emails.

The application follows a multi-stage approval workflow, ensuring every request is reviewed, tracked, and audited from creation until completion.

---

## Features

### Request Management
- Create new access requests
- View submitted requests
- Track request status in real time
- View approval history
- Respond to requests for additional information

### Approval Workflow
- Multi-stage approval process
- Approve or reject requests
- Return requests for more information
- Add comments during approvals
- Automatic workflow progression

### Workflow Engine
- Supports multiple approval stages
- Prevents invalid workflow transitions
- Tracks the current request owner
- Stores complete workflow history
- Maintains audit logs for every action

### Dashboard
- View pending approvals
- View completed requests
- Monitor request progress
- Timeline of workflow actions

---

## Workflow

```text
Employee
    │
    ▼
Create Request
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

At each stage an approver can:

- Approve
- Reject
- Request More Information

---

## Tech Stack

### Backend
- Django
- Django REST Framework
- SQLite / PostgreSQL
- REST APIs

### Frontend
- Angular
- TypeScript
- HTML
- CSS

---

## Project Structure

```
backend/
    apps/
    models/
    views/
    serializers/
    urls/

frontend/
    src/
        app/
        components/
        services/
```

---

## API Features

- RESTful API
- CRUD operations
- Workflow validation
- Role-based authorization
- Error handling
- Audit logging

---

## Main Pages

- Dashboard
- Create Request
- My Requests
- Request Details
- Pending Approvals
- Approval Details

---

## Business Rules

- Only valid workflow transitions are allowed.
- Every workflow action is logged.
- Current approver is tracked.
- Approval history cannot be modified.
- Requests can be approved, rejected, or returned for more information.

---

## Installation

### Clone the repository

```bash
git clone https://github.com/yourusername/AccessRequestWorkflow.git
cd AccessRequestWorkflow
```

### Backend

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

### Frontend

```bash
cd frontend

npm install

ng serve
```

---

## Future Improvements

- Email notifications
- JWT Authentication
- Role management
- File attachments
- Admin dashboard
- Analytics
- Docker support
- CI/CD pipeline

---

## Screenshots

> Add screenshots of:
>
> - Dashboard
> - Request Form
> - Approval Page
> - Request Timeline

---

## Author

**Ali Osama**

GitHub: https://github.com/ali0sama

LinkedIn: https://www.linkedin.com/in/ali-osama-7673b2352/

---

## License

This project is for learning purposes as part of a workflow onboarding project.
