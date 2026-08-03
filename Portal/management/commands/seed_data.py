from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Portal.models import (
    Profile,
    Application,
    AccessRequest,
    WorkflowHistory,
    Role,
    State,
    Action,
)


class Command(BaseCommand):
    help = "Seeds the database with test users, applications, and access requests."

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # ── Users ─────────────────────────────────────────────────────────────

        requester1 = self._make_user("emma.watson", "pass1234")
        manager1 = self._make_user("james.carter", "pass1234")
        appowner1 = self._make_user("olivia.chen", "pass1234")
        security1 = self._make_user("noah.patel", "pass1234")

        self._make_profile(requester1, Role.REQUESTER, manager=manager1)
        self._make_profile(manager1, Role.MANAGER)
        self._make_profile(appowner1, Role.APP_OWNER)
        self._make_profile(security1, Role.SECURITY)

        # ── Applications ──────────────────────────────────────────────────────

        github = self._make_app(
            "GitHub Enterprise",
            appowner1,
            "Source control and CI/CD platform used by engineering.",
        )
        jira = self._make_app(
            "Jira", appowner1, "Issue tracking and project management platform."
        )
        aws = self._make_app(
            "AWS Console",
            appowner1,
            "Cloud infrastructure console for provisioning and billing.",
        )

        # ── Requests (states set directly — no permission checks needed for seed data) ─

        # 1. DRAFT
        self._make_request(
            requester1,
            jira,
            "Need access to track my team's sprint tickets.",
            State.DRAFT,
            current_owner=None,
            history=[],
        )

        # 2. PENDING_MANAGER
        self._make_request(
            requester1,
            github,
            "Required to push code for the new mobile app project.",
            State.PENDING_MANAGER,
            current_owner=manager1,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
            ],
        )

        # 3. PENDING_APP_OWNER
        self._make_request(
            requester1,
            aws,
            "Need access to deploy to the staging S3 bucket.",
            State.PENDING_APP_OWNER,
            current_owner=appowner1,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (
                    State.PENDING_MANAGER,
                    State.PENDING_APP_OWNER,
                    Action.APPROVE,
                    manager1,
                    "Approved — legitimate business need.",
                ),
            ],
        )

        # 4. APPROVED (full workflow)
        self._make_request(
            requester1,
            jira,
            "Permanent access needed for cross-team reporting duties.",
            State.APPROVED,
            current_owner=None,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (
                    State.PENDING_MANAGER,
                    State.PENDING_APP_OWNER,
                    Action.APPROVE,
                    manager1,
                    "Confirmed with team lead.",
                ),
                (
                    State.PENDING_APP_OWNER,
                    State.PENDING_SECURITY,
                    Action.APPROVE,
                    appowner1,
                    "Access level is appropriate.",
                ),
                (
                    State.PENDING_SECURITY,
                    State.APPROVED,
                    Action.APPROVE,
                    security1,
                    "Security review passed.",
                ),
            ],
        )

        # 5. REJECTED
        self._make_request(
            requester1,
            github,
            "Temporary access for a hackathon project.",
            State.REJECTED,
            current_owner=None,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (
                    State.PENDING_MANAGER,
                    State.REJECTED,
                    Action.REJECT,
                    manager1,
                    "Hackathon repo already has open access, no need for full org access.",
                ),
            ],
        )

        # 6. INFO_REQUESTED
        self._make_request(
            requester1,
            aws,
            "Access needed for the Project Atlas migration work.",
            State.INFO_REQUESTED,
            current_owner=requester1,
            returned_from_state=State.PENDING_MANAGER,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (
                    State.PENDING_MANAGER,
                    State.INFO_REQUESTED,
                    Action.RETURN,
                    manager1,
                    "Please specify which AWS accounts/regions you need.",
                ),
            ],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nDone!\n"
                "  Users        : emma.watson, james.carter, olivia.chen, noah.patel  (password: pass1234)\n"
                "  Applications : GitHub Enterprise, Jira, AWS Console\n"
                "  Requests     : DRAFT, PENDING_MANAGER, PENDING_APP_OWNER, APPROVED, REJECTED, INFO_REQUESTED\n"
            )
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_user(self, username, password):
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
        return user

    def _make_profile(self, user, role, manager=None):
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.manager = manager
        profile.save()
        return profile

    def _make_app(self, name, owner, description=""):
        app, _ = Application.objects.get_or_create(
            name=name,
            defaults={
                "owner": owner,
                "description": description,
            },
        )
        return app

    def _make_request(
        self,
        requester,
        application,
        justification,
        state,
        current_owner,
        history,
        returned_from_state=None,
    ):
        req = AccessRequest.objects.create(
            requester=requester,
            application=application,
            justification=justification,
            current_state=state,
            current_owner=current_owner,
            returned_from_state=returned_from_state,
        )
        for from_state, to_state, action, actor, comment in history:
            WorkflowHistory.objects.create(
                request=req,
                from_state=from_state,
                to_state=to_state,
                action=action,
                actor=actor,
                comment=comment,
            )
        return req
