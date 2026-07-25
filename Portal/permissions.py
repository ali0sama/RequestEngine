from rest_framework.permissions import BasePermission
from .models import AccessRequest
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
