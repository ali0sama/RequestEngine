# from django.shortcuts import render
# from django.http import HttpResponse
# Create your views here.
# def home(request):
#     return HttpResponse('<h1>This is the Portal Homepage</h1>')
import logging

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .exceptions import InvalidTransitionError, UnauthorizedActionError
from .models import AccessRequest, Application, State
from .models import Action as WorkflowAction
from .permissions import (
    IsApproverRole,
    IsCurrentOwner,
    IsRequester,
    IsRequesterOrCurrentOwner,
)
from .serializers import (
    AccessRequestSerializer,
    ApplicationSerializer,
    ChangePasswordSerializer,
    LoginResponseSerializer,
    LogoutSerializer,
    RefreshResponseSerializer,
    UserSerializer,
    WorkflowActionSerializer,
    WorkflowHistorySerializer,
)
from .services import apply_transition

audit_logger = logging.getLogger("portal.audit")


@extend_schema(
    tags=["Authentication"],
    summary="Login",
    description="Authenticates a user with username and password, returning an access and refresh token pair.",
    responses={200: LoginResponseSerializer},
)
class AuthLoginView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            audit_logger.info("Login succeeded for username=%s", request.data.get("username"))
        return response


@extend_schema(
    tags=["Authentication"],
    summary="Refresh Access Token",
    description="Exchanges a valid refresh token for a new access token.",
    responses={200: RefreshResponseSerializer},
)
class AuthRefreshView(TokenRefreshView):
    pass


@extend_schema(
    tags=["Authentication"],
    summary="Get Current User",
    description="Returns the profile of the currently authenticated user, including their workflow role.",
    responses={200: UserSerializer},
)
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request) -> Response:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(
    tags=["Authentication"],
    summary="Change Password",
    description="Allows the authenticated user to change their own password.",
    request=ChangePasswordSerializer,
    responses={200: dict, 400: dict},
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not request.user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=request.user)
        except DjangoValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        request.user.set_password(new_password)
        request.user.save()
        return Response({"detail": "Password updated successfully"})


@extend_schema(
    tags=["Authentication"],
    summary="Logout",
    description="Blacklists the given refresh token, preventing it from being used to obtain new access tokens.",
    request=LogoutSerializer,
    responses={200: dict, 400: dict},
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid or already-blacklisted token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"detail": "Logged out successfully"})


class AccessRequestViewSet(viewsets.ModelViewSet):
    serializer_class = AccessRequestSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        if self.action in [
            "approve",
            "reject",
            "return_for_info",
            "submit",
            "resubmit",
            "retrieve",
            "history",
        ]:
            return AccessRequest.objects.all()
        return AccessRequest.objects.filter(requester=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsAuthenticated(), IsRequesterOrCurrentOwner()]
        if self.action in ["submit", "resubmit"]:
            return [IsAuthenticated(), IsRequester()]
        if self.action in ["approve", "reject", "return_for_info"]:
            return [IsAuthenticated(), IsCurrentOwner()]
        if self.action == "pending_approvals":
            return [IsAuthenticated(), IsApproverRole()]
        if self.action == "needs_my_response":
            return [IsAuthenticated()]
        return super().get_permissions()

    @extend_schema(
        summary="Create Access Request",
        description="Creates a new access request for an application. The requester is set automatically from the authenticated user; the request starts in DRAFT state.",
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="List My Requests",
        description="Returns every access request submitted by the currently authenticated user.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Request Details",
        description="Returns full details of a specific access request, including its complete approval history, for either the requester or the current approver.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Pending Approvals",
        description="Returns every access request currently awaiting a decision from the authenticated approver.",
    )
    @action(detail=False, methods=["get"])
    def pending_approvals(self, request: Request) -> Response:
        qs = AccessRequest.objects.filter(current_owner=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Submit Request",
        description="Moves a DRAFT request into the approval chain, assigning it to the requester's line manager. Only callable by the request's own creator.",
        request=WorkflowActionSerializer,
        responses={200: AccessRequestSerializer, 400: dict},
    )
    @action(detail=True, methods=["post"])
    def submit(self, request: Request, pk=None):
        return self._handle_action(request, WorkflowAction.SUBMIT)

    @extend_schema(
        summary="Approve Request",
        description="Approves a request currently assigned to the logged-in user, advancing it to the next stage.",
        request=WorkflowActionSerializer,
        responses={200: AccessRequestSerializer},
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.APPROVE)

    @extend_schema(
        summary="Reject Request",
        description="Rejects a request currently assigned to the logged-in user, ending its workflow.",
        request=WorkflowActionSerializer,
        responses={200: AccessRequestSerializer, 400: dict, 403: dict},
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.REJECT)

    @extend_schema(
        summary="Return for Information",
        description="Sends a request back to its original requester for clarification, remembering the current stage so it can resume there after resubmission.",
        request=WorkflowActionSerializer,
        responses={200: AccessRequestSerializer, 400: dict, 403: dict},
    )
    @action(detail=True, methods=["post"])
    def return_for_info(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.RETURN)

    @extend_schema(
        summary="Resubmit Request",
        description="Called by the original requester after responding to a return-for-info request. Resumes the workflow at the stage it was returned from.",
        request=WorkflowActionSerializer,
        responses={200: AccessRequestSerializer, 400: dict, 403: dict},
    )
    @action(detail=True, methods=["post"])
    def resubmit(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.RESUBMIT)

    @extend_schema(
        summary="Get Approval History",
        description="Returns the full chronological list of workflow actions taken on a specific request.",
        responses={200: WorkflowHistorySerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        access_request = self.get_object()
        serializer = WorkflowHistorySerializer(access_request.history.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Needs My Response",
        description="Returns every access request submitted by this user that has been returned for more information and requires a response.",
    )
    @action(detail=False, methods=["get"])
    def needs_my_response(self, request):
        qs = AccessRequest.objects.filter(
            requester=request.user,
            current_state=State.INFO_REQUESTED,
        )
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    def _handle_action(self, request, workflow_action):
        access_request = self.get_object()
        comment = request.data.get("comment", "")

        try:
            updated = apply_transition(
                access_request, workflow_action, request.user, comment
            )
        except InvalidTransitionError as e:
            audit_logger.warning(
                "Invalid transition denied: request=%s action=%s actor=%s state=%s: %s",
                access_request.id, workflow_action, request.user,
                access_request.current_state, e,
            )
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except UnauthorizedActionError as e:
            audit_logger.warning(
                "Unauthorized action denied: request=%s action=%s actor=%s: %s",
                access_request.id, workflow_action, request.user, e,
            )
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(updated)
        return Response(serializer.data)

    def permission_denied(self, request, message=None, code=None):
        audit_logger.warning(
            "Permission denied: user=%s action=%s path=%s",
            request.user, self.action, request.path,
        )
        super().permission_denied(request, message=message, code=code)


class ApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()

    @extend_schema(
        summary="List Applications",
        description="Returns every internal application available for access requests.",
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get Application Details",
        description="Returns details of a single internal application.",
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
