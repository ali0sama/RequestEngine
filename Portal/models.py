from django.conf import settings
from django.db import models


class Role(models.TextChoices):
    REQUESTER = 'REQUESTER', 'Requester'
    MANAGER = 'MANAGER', 'Line Manager'
    APP_OWNER = 'APP_OWNER', 'Application Owner'
    SECURITY = 'SECURITY', 'Security Team'


class State(models.TextChoices):
    DRAFT = 'DRAFT', 'Draft'
    PENDING_MANAGER = 'PENDING_MANAGER', 'Pending Manager'
    PENDING_APP_OWNER = 'PENDING_APP_OWNER', 'Pending Application Owner'
    PENDING_SECURITY = 'PENDING_SECURITY', 'Pending Security'
    INFO_REQUESTED = 'INFO_REQUESTED', 'Info Requested'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'


class Action(models.TextChoices):
    SUBMIT = 'SUBMIT', 'Submit'
    APPROVE = 'APPROVE', 'Approve'
    REJECT = 'REJECT', 'Reject'
    RETURN = 'RETURN', 'Return for Info'
    RESUBMIT = 'RESUBMIT', 'Resubmit'
    
class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile')
    role=models.CharField(max_length=30,choices=Role.choices)
    manager=models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Application(models.Model):
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_applications'
    )
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class AccessRequest(models.Model):
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_requests'
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.PROTECT,
        related_name='requests'
    )
    justification = models.TextField()
    current_state = models.CharField(
        max_length=30,
        choices=State.choices,
        default=State.DRAFT
    )
    current_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_requests'
    )
    returned_from_state = models.CharField(max_length=30, null=True, blank=True,choices=State.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.requester.username} → {self.application.name} ({self.current_state})"

class WorkflowHistory(models.Model):
    request = models.ForeignKey(
        AccessRequest,
        on_delete=models.CASCADE,
        related_name='history'
    )
    from_state = models.CharField(max_length=30,choices=State.choices)
    to_state = models.CharField(max_length=30,choices=State.choices)
    action = models.CharField(max_length=20, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='workflow_actions'
    )
    comment = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.request_id}: {self.from_state} → {self.to_state} ({self.action})"