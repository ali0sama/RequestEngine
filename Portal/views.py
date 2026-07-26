# from django.shortcuts import render
# from django.http import HttpResponse
# Create your views here.
# def home(request):
#     return HttpResponse('<h1>This is the Portal Homepage</h1>')
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema

from .serializers import (
    UserSerializer,
    LoginResponseSerializer,
    RefreshResponseSerializer,
    ChangePasswordSerializer,
    LogoutSerializer,
    WorkflowActionSerializer,
)


from .models import AccessRequest, Application, State, Action as WorkflowAction
from .serializers import (
    AccessRequestSerializer,
    ApplicationSerializer,
    WorkflowHistorySerializer,
)
from .services import apply_transition
from .exceptions import InvalidTransitionError, UnauthorizedActionError
from .permissions import (
    IsApproverRole,
    IsRequesterOrCurrentOwner,
    IsCurrentOwner,
    IsRequester,
    IsRequesterRole,
)


@extend_schema(
    tags=["Authentication"],
    summary="Login",
    description="Authenticates a user with username and password, returning an access and refresh token pair.",
    responses={200: LoginResponseSerializer},
)
class AuthLoginView(TokenObtainPairView):
    pass


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
            return [IsAuthenticated(), IsRequesterRole()]
        return super().get_permissions()

    @action(detail=False, methods=["get"])
    def pending_approvals(self, request: Request) -> Response:
        qs = AccessRequest.objects.filter(current_owner=request.user)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=WorkflowActionSerializer, responses={200: AccessRequestSerializer}
    )
    @action(detail=True, methods=["post"])
    def submit(self, request: Request, pk=None):
        return self._handle_action(request, WorkflowAction.SUBMIT)

    @extend_schema(
        request=WorkflowActionSerializer, responses={200: AccessRequestSerializer}
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.APPROVE)

    @extend_schema(
        request=WorkflowActionSerializer, responses={200: AccessRequestSerializer}
    )
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.REJECT)

    @extend_schema(
        request=WorkflowActionSerializer, responses={200: AccessRequestSerializer}
    )
    @action(detail=True, methods=["post"])
    def return_for_info(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.RETURN)

    @extend_schema(
        request=WorkflowActionSerializer, responses={200: AccessRequestSerializer}
    )
    @action(detail=True, methods=["post"])
    def resubmit(self, request, pk=None):
        return self._handle_action(request, WorkflowAction.RESUBMIT)

    @action(detail=True, methods=["get"])
    def history(self, request, pk=None):
        access_request = self.get_object()
        serializer = WorkflowHistorySerializer(access_request.history.all(), many=True)
        return Response(serializer.data)

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
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except UnauthorizedActionError as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(updated)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    queryset = Application.objects.all()
