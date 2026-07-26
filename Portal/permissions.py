from rest_framework.permissions import BasePermission
from .models import AccessRequest, Role
from rest_framework.request import Request
from rest_framework.views import APIView


class IsRequesterOrCurrentOwner(BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: AccessRequest
    ) -> bool:
        return obj.requester == request.user or obj.current_owner == request.user


class IsCurrentOwner(BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: AccessRequest
    ) -> bool:
        return obj.current_owner == request.user


class IsRequester(BasePermission):
    def has_object_permission(
        self, request: Request, view: APIView, obj: AccessRequest
    ) -> bool:
        return obj.requester == request.user


class IsApproverRole(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.profile.role in [
            Role.MANAGER,
            Role.APP_OWNER,
            Role.SECURITY,
        ]


class IsRequesterRole(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.profile.role == Role.REQUESTER
