from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from Portal.models import Profile, Application, AccessRequest, WorkflowHistory, Role, State, Action


class Command(BaseCommand):
    help = 'Seeds the database with test users, applications, and access requests.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # ── Users ─────────────────────────────────────────────────────────────

        requester1 = self._make_user('requester1', 'pass1234')
        manager1   = self._make_user('manager1',   'pass1234')
        appowner1  = self._make_user('appowner1',  'pass1234')
        security1  = self._make_user('security1',  'pass1234')

        self._make_profile(requester1, Role.REQUESTER, manager=manager1)
        self._make_profile(manager1,   Role.MANAGER)
        self._make_profile(appowner1,  Role.APP_OWNER)
        self._make_profile(security1,  Role.SECURITY)

        # ── Applications ──────────────────────────────────────────────────────

        sap        = self._make_app('SAP ERP',        appowner1, 'Core ERP system for finance and HR.')
        salesforce = self._make_app('Salesforce CRM', appowner1, 'Customer relationship management platform.')
        azure      = self._make_app('Azure Portal',   appowner1, 'Cloud infrastructure management console.')

        # ── Requests (states set directly — no permission checks needed for seed data) ─

        # 1. DRAFT
        self._make_request(
            requester1, sap,
            'Need read access for monthly reporting.',
            State.DRAFT, current_owner=None,
            history=[]
        )

        # 2. PENDING_MANAGER
        self._make_request(
            requester1, salesforce,
            'Required for managing client accounts in Q3.',
            State.PENDING_MANAGER, current_owner=manager1,
            history=[
                (State.DRAFT, State.PENDING_MANAGER, Action.SUBMIT, requester1, ''),
            ]
        )

        # 3. PENDING_APP_OWNER
        self._make_request(
            requester1, azure,
            'Need access to deploy staging environments.',
            State.PENDING_APP_OWNER, current_owner=appowner1,
            history=[
                (State.DRAFT,            State.PENDING_MANAGER,   Action.SUBMIT,  requester1, ''),
                (State.PENDING_MANAGER,  State.PENDING_APP_OWNER, Action.APPROVE, manager1,   'Approved — legitimate business need.'),
            ]
        )

        # 4. APPROVED (full workflow)
        self._make_request(
            requester1, sap,
            'Permanent access needed for audit team.',
            State.APPROVED, current_owner=None,
            history=[
                (State.DRAFT,             State.PENDING_MANAGER,   Action.SUBMIT,  requester1, ''),
                (State.PENDING_MANAGER,   State.PENDING_APP_OWNER, Action.APPROVE, manager1,   'Confirmed with team lead.'),
                (State.PENDING_APP_OWNER, State.PENDING_SECURITY,  Action.APPROVE, appowner1,  'Access level is appropriate.'),
                (State.PENDING_SECURITY,  State.APPROVED,          Action.APPROVE, security1,  'Security review passed.'),
            ]
        )

        # 5. REJECTED
        self._make_request(
            requester1, salesforce,
            'Temp access for demo.',
            State.REJECTED, current_owner=None,
            history=[
                (State.DRAFT,           State.PENDING_MANAGER, Action.SUBMIT, requester1, ''),
                (State.PENDING_MANAGER, State.REJECTED,        Action.REJECT, manager1,   'Demo can be done with existing permissions.'),
            ]
        )

        # 6. INFO_REQUESTED
        self._make_request(
            requester1, azure,
            'Access for project delta migration work.',
            State.INFO_REQUESTED, current_owner=requester1,
            returned_from_state=State.PENDING_MANAGER,
            history=[
                (State.DRAFT,           State.PENDING_MANAGER, Action.SUBMIT,  requester1, ''),
                (State.PENDING_MANAGER, State.INFO_REQUESTED,  Action.RETURN,  manager1,   'Please clarify which resources you need access to.'),
            ]
        )

        self.stdout.write(self.style.SUCCESS(
            '\nDone!\n'
            '  Users        : requester1, manager1, appowner1, security1  (password: pass1234)\n'
            '  Applications : SAP ERP, Salesforce CRM, Azure Portal\n'
            '  Requests     : DRAFT, PENDING_MANAGER, PENDING_APP_OWNER, APPROVED, REJECTED, INFO_REQUESTED\n'
        ))

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

    def _make_app(self, name, owner, description=''):
        app, _ = Application.objects.get_or_create(name=name, defaults={
            'owner': owner,
            'description': description,
        })
        return app

    def _make_request(self, requester, application, justification,
                      state, current_owner, history,
                      returned_from_state=None):
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
