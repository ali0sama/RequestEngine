from django.db import transaction
from .models import AccessRequest, State, Action, WorkflowHistory
from .constants import TRANSITIONS
from .exceptions import InvalidTransitionError, UnauthorizedActionError
from django.contrib.auth import get_user_model


User = get_user_model()


def apply_transition(
    access_request: AccessRequest, action: Action, actor, comment: str = ""
) -> AccessRequest:
    if action == Action.RESUBMIT:
        if access_request.current_state != State.INFO_REQUESTED:
            raise InvalidTransitionError("Can only resubmit from INFO_REQUESTED")
        if access_request.requester != actor:
            raise UnauthorizedActionError("Only the requester can resubmit")
        new_state = access_request.returned_from_state
        new_owner = _owner_for_state(access_request, new_state)

        with transaction.atomic():
            WorkflowHistory.objects.create(
                request=access_request,
                from_state=access_request.current_state,
                to_state=new_state,
                action=action,
                actor=actor,
                comment=comment,
            )
            access_request.current_state = new_state
            access_request.current_owner = new_owner
            access_request.returned_from_state = None
            access_request.save()

        return access_request
    lookup_key = (access_request.current_state, action)
    if lookup_key not in TRANSITIONS:
        raise InvalidTransitionError(
            f"Cannot perform {action} from {access_request.current_state}"
        )
    new_state, required_role = TRANSITIONS[lookup_key]

    # SUBMIT: any role may submit their own request — IsRequester DRF permission
    # already verified actor == access_request.requester before we get here.
    if action == Action.SUBMIT:
        if actor != access_request.requester:
            raise UnauthorizedActionError(
                f"{actor} did not create this request"
            )
    else:
        if actor.profile.role != required_role or actor != access_request.current_owner:
            raise UnauthorizedActionError(
                f"{actor} is not authorized to {action} this request"
            )

    new_owner = _owner_for_state(access_request, new_state)

    # If the requester has no manager, skip the manager stage and go to app owner.
    if action == Action.SUBMIT and new_state == State.PENDING_MANAGER and new_owner is None:
        new_state = State.PENDING_APP_OWNER
        new_owner = _owner_for_state(access_request, new_state)

    if new_owner is None and new_state not in (State.APPROVED, State.REJECTED):
        raise InvalidTransitionError(
            f"Cannot move this request to {new_state}: no eligible owner could be found "
            f"(check that a manager/application owner/security team member is properly assigned)"
        )
    returned_from = access_request.current_state if action == Action.RETURN else None
    with transaction.atomic():
        WorkflowHistory.objects.create(
            request=access_request,
            from_state=access_request.current_state,
            to_state=new_state,
            action=action,
            actor=actor,
            comment=comment,
        )
        access_request.current_state = new_state
        access_request.current_owner = new_owner
        access_request.returned_from_state = returned_from
        access_request.save()

    return access_request


def _owner_for_state(access_request: AccessRequest, state: str) -> User | None:
    from .models import Role

    match state:
        case State.PENDING_MANAGER:
            return access_request.requester.profile.manager
        case State.PENDING_APP_OWNER:
            return access_request.application.owner
        case State.PENDING_SECURITY:
            return User.objects.filter(profile__role=Role.SECURITY).first()
        case State.INFO_REQUESTED:
            return access_request.requester
        case _:
            return None
