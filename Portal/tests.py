from django.contrib.auth.models import User
from django.test import TestCase

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
