from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from Portal.exceptions import InvalidTransitionError, UnauthorizedActionError
from Portal.models import AccessRequest, Action, Application, Profile, Role, State
from Portal.services import apply_transition


class ApplyTransitionTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user("manager1", password="pass1234")
        Profile.objects.create(user=self.manager, role=Role.MANAGER)

        self.requester = User.objects.create_user("requester1", password="pass1234")
        Profile.objects.create(
            user=self.requester, role=Role.REQUESTER, manager=self.manager
        )

        self.app_owner = User.objects.create_user("appowner1", password="pass1234")
        Profile.objects.create(user=self.app_owner, role=Role.APP_OWNER)

        self.application = Application.objects.create(
            name="Jira", owner=self.app_owner, description="Issue tracking"
        )

    def test_submit_moves_to_pending_manager(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.DRAFT,
        )

        updated = apply_transition(req, Action.SUBMIT, self.requester)

        self.assertEqual(updated.current_state, State.PENDING_MANAGER)
        self.assertEqual(updated.current_owner, self.manager)

    def test_wrong_role_cannot_approve(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.PENDING_MANAGER,
            current_owner=self.manager,
        )

        with self.assertRaises(UnauthorizedActionError):
            apply_transition(req, Action.APPROVE, self.requester)

    def test_invalid_transition_from_terminal_state(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.APPROVED,
        )

        with self.assertRaises(InvalidTransitionError):
            apply_transition(req, Action.SUBMIT, self.requester)

    def test_submit_logs_transition(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.DRAFT,
        )

        with self.assertLogs("portal.audit", level="INFO") as cm:
            apply_transition(req, Action.SUBMIT, self.requester)

        self.assertTrue(any("SUBMIT" in line and str(req.id) in line for line in cm.output))


class ProfileManagerValidationTests(TestCase):
    def test_manager_field_must_have_manager_role(self):
        requester = User.objects.create_user("bad_manager_test", password="pass1234")
        Profile.objects.create(user=requester, role=Role.REQUESTER)

        subordinate = User.objects.create_user("subordinate_test", password="pass1234")
        profile = Profile(user=subordinate, role=Role.REQUESTER, manager=requester)

        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_manager_field_accepts_actual_manager(self):
        manager = User.objects.create_user("real_manager_test", password="pass1234")
        Profile.objects.create(user=manager, role=Role.MANAGER)

        subordinate = User.objects.create_user("subordinate2_test", password="pass1234")
        profile = Profile(user=subordinate, role=Role.REQUESTER, manager=manager)

        profile.full_clean()  # should not raise


class AuditLoggingApiTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user("manager1", password="pass1234")
        Profile.objects.create(user=self.manager, role=Role.MANAGER)

        self.requester = User.objects.create_user("requester1", password="pass1234")
        Profile.objects.create(
            user=self.requester, role=Role.REQUESTER, manager=self.manager
        )

        self.app_owner = User.objects.create_user("appowner1", password="pass1234")
        Profile.objects.create(user=self.app_owner, role=Role.APP_OWNER)

        self.application = Application.objects.create(
            name="Jira", owner=self.app_owner, description="Issue tracking"
        )

        self.client = APIClient()

    def test_invalid_transition_via_api_logs_warning(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.REJECTED,
        )
        self.client.force_authenticate(user=self.requester)

        with self.assertLogs("portal.audit", level="WARNING") as cm:
            response = self.client.post(f"/api/requests/{req.id}/submit/")

        self.assertEqual(response.status_code, 400)
        self.assertTrue(any("Invalid transition denied" in line for line in cm.output))

    def test_permission_denied_via_api_logs_warning(self):
        req = AccessRequest.objects.create(
            requester=self.requester,
            application=self.application,
            justification="Need access",
            current_state=State.PENDING_MANAGER,
            current_owner=self.manager,
        )
        self.client.force_authenticate(user=self.requester)

        with self.assertLogs("portal.audit", level="WARNING") as cm:
            response = self.client.post(f"/api/requests/{req.id}/approve/")

        self.assertEqual(response.status_code, 403)
        self.assertTrue(any("Permission denied" in line for line in cm.output))

    def test_failed_login_logs_warning(self):
        with self.assertLogs("portal.audit", level="WARNING") as cm:
            response = self.client.post(
                "/api/auth/login/",
                {"username": "requester1", "password": "wrong-password"},
            )

        self.assertEqual(response.status_code, 401)
        self.assertTrue(any("Login failed" in line for line in cm.output))

    def test_successful_login_logs_info(self):
        with self.assertLogs("portal.audit", level="INFO") as cm:
            response = self.client.post(
                "/api/auth/login/",
                {"username": "requester1", "password": "pass1234"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(any("Login succeeded" in line for line in cm.output))
