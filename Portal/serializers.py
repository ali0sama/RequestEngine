from rest_framework import serializers
from .models import Application, AccessRequest, WorkflowHistory
from django.contrib.auth.models import User


class WorkflowHistorySerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source="actor.username", read_only=True)

    class Meta:
        model = WorkflowHistory
        fields = [
            "id",
            "from_state",
            "to_state",
            "action",
            "actor",
            "actor_username",
            "comment",
            "timestamp",
        ]
        read_only_fields = fields


class ApplicationSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "name", "owner", "owner_username", "description"]
        read_only_fields = fields


class AccessRequestSerializer(serializers.ModelSerializer):
    history = WorkflowHistorySerializer(many=True, read_only=True)
    requester_username = serializers.CharField(
        source="requester.username", read_only=True
    )
    current_owner_username = serializers.CharField(
        source="current_owner.username", read_only=True
    )
    application_name = serializers.CharField(source="application.name", read_only=True)

    class Meta:
        model = AccessRequest
        fields = [
            "id",
            "requester",
            "requester_username",
            "application",
            "application_name",
            "justification",
            "current_state",
            "current_owner",
            "current_owner_username",
            "returned_from_state",
            "created_at",
            "updated_at",
            "history",
        ]
        read_only_fields = [
            "requester",
            "current_state",
            "current_owner",
            "returned_from_state",
            "created_at",
            "updated_at",
        ]


class WorkflowActionSerializer(serializers.Serializer):
    comment = serializers.CharField(required=False, allow_blank=True)


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class RefreshResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source="profile.role", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
