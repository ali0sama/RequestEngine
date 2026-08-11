from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from Portal.models import (
    AccessRequest,
    Action,
    Application,
    Profile,
    Role,
    State,
    WorkflowHistory,
)


class Command(BaseCommand):
    help = "Seeds the database with test users, applications, and access requests."

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # ── Users ─────────────────────────────────────────────────────────────

        manager = self._make_user("daniel.foster", "pass1234")
        requester1 = self._make_user("olivia.bennett", "pass1234")
        requester2 = self._make_user("marcus.reyes", "pass1234")
        requester_no_manager = self._make_user("zara.khalil", "pass1234")
        appowner1 = self._make_user("priya.nair", "pass1234")
        appowner2 = self._make_user("lucas.moreau", "pass1234")
        security1 = self._make_user("sophia.becker", "pass1234")

        self._make_profile(manager, Role.MANAGER)
        self._make_profile(requester1, Role.REQUESTER, manager=manager)
        self._make_profile(requester2, Role.REQUESTER, manager=manager)
        self._make_profile(requester_no_manager, Role.REQUESTER, manager=None)
        self._make_profile(appowner1, Role.APP_OWNER)
        self._make_profile(appowner2, Role.APP_OWNER)
        self._make_profile(security1, Role.SECURITY)

        # ── Applications ──────────────────────────────────────────────────────

        slack = self._make_app(
            "Slack", appowner1,
            "Team messaging and collaboration platform.",
            logo="images/app-logos/slack.png",
        )
        jira = self._make_app(
            "Jira", appowner1,
            "Issue tracking and project management platform.",
            logo="images/app-logos/jira.png",
        )
        confluence = self._make_app(
            "Confluence", appowner1,
            "Team knowledge base and documentation.",
            logo="images/app-logos/confluence.png",
        )
        zoom = self._make_app(
            "Zoom", appowner1,
            "Video conferencing and meetings.",
            logo="images/app-logos/zoom.png",
        )
        github = self._make_app(
            "GitHub Enterprise", appowner2,
            "Source control and CI/CD platform used by engineering.",
            logo="images/app-logos/github.png",
        )
        aws = self._make_app(
            "AWS Console", appowner2,
            "Cloud infrastructure console for provisioning and billing.",
            logo="images/app-logos/aws.png",
        )
        salesforce = self._make_app(
            "Salesforce", appowner2,
            "Customer relationship management platform.",
            logo="images/app-logos/salesforce.png",
        )
        okta = self._make_app(
            "Okta", appowner2,
            "Identity and access management platform.",
            logo="images/app-logos/okta.png",
        )

        # ── Requests (states set directly — no permission checks needed for seed data) ─

        # 1. DRAFT
        self._make_request(
            requester1, slack,
            "Need Slack access to join the platform engineering channels.",
            State.DRAFT, current_owner=None,
            history=[],
        )

        # 2. PENDING_MANAGER
        self._make_request(
            requester2, jira,
            "Need to track my team's sprint tickets.",
            State.PENDING_MANAGER, current_owner=manager,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester2, ""),
            ],
        )

        # 3. PENDING_APP_OWNER
        self._make_request(
            requester1, confluence,
            "Need access to publish onboarding documentation.",
            State.PENDING_APP_OWNER, current_owner=appowner1,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (State.PENDING_MANAGER, State.PENDING_APP_OWNER, Action.APPROVE, manager,
                 "Approved — legitimate business need."),
            ],
        )

        # 4. PENDING_SECURITY
        self._make_request(
            requester2, github,
            "Required to push code for the new mobile app project.",
            State.PENDING_SECURITY, current_owner=security1,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester2, ""),
                (State.PENDING_MANAGER, State.PENDING_APP_OWNER, Action.APPROVE, manager,
                 "Confirmed with team lead."),
                (State.PENDING_APP_OWNER, State.PENDING_SECURITY, Action.APPROVE, appowner2,
                 "Access level is appropriate."),
            ],
        )

        # 5. APPROVED (full workflow)
        self._make_request(
            requester1, aws,
            "Permanent access needed for the platform team's on-call rotation.",
            State.APPROVED, current_owner=None,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (State.PENDING_MANAGER, State.PENDING_APP_OWNER, Action.APPROVE, manager,
                 "Confirmed with team lead."),
                (State.PENDING_APP_OWNER, State.PENDING_SECURITY, Action.APPROVE, appowner2,
                 "Access level is appropriate."),
                (State.PENDING_SECURITY, State.APPROVED, Action.APPROVE, security1,
                 "Security review passed."),
            ],
        )

        # 6. REJECTED
        self._make_request(
            requester2, salesforce,
            "Temporary access for a demo environment.",
            State.REJECTED, current_owner=None,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester2, ""),
                (State.PENDING_MANAGER, State.REJECTED, Action.REJECT, manager,
                 "Demo can be done with existing sandbox access, no need for full org access."),
            ],
        )

        # 7. INFO_REQUESTED
        self._make_request(
            requester1, okta,
            "Access needed for the SSO migration project.",
            State.INFO_REQUESTED, current_owner=requester1,
            returned_from_state=State.PENDING_APP_OWNER,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ""),
                (State.PENDING_MANAGER, State.PENDING_APP_OWNER, Action.APPROVE, manager,
                 "Approved — legitimate business need."),
                (State.PENDING_APP_OWNER, State.INFO_REQUESTED, Action.RETURN, appowner2,
                 "Please specify which applications need SSO enabled."),
            ],
        )

        # 8. Manager-skip case — requester has no manager, SUBMIT jumps straight to PENDING_APP_OWNER
        self._make_request(
            requester_no_manager, zoom,
            "Need Zoom access for client-facing calls.",
            State.PENDING_APP_OWNER, current_owner=appowner1,
            history=[
                (State.DRAFT, State.PENDING_APP_OWNER, Action.SUBMIT, requester_no_manager, ""),
            ],
        )

        self.stdout.write(
            self.style.SUCCESS(
                "\nDone!\n"
                "  Users        : daniel.foster (manager), olivia.bennett, marcus.reyes,\n"
                "                 zara.khalil (no manager), priya.nair, lucas.moreau (app owners),\n"
                "                 sophia.becker (security)  — password: pass1234\n"
                "  Applications : Slack, Jira, Confluence, Zoom, GitHub Enterprise,\n"
                "                 AWS Console, Salesforce, Okta\n"
                "  Requests     : DRAFT, PENDING_MANAGER, PENDING_APP_OWNER, PENDING_SECURITY,\n"
                "                 APPROVED, REJECTED, INFO_REQUESTED, and a manager-skip case\n"
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

    def _make_app(self, name, owner, description="", logo=""):
        app, _ = Application.objects.get_or_create(
            name=name,
            defaults={
                "owner": owner,
                "description": description,
                "logo": logo,
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
