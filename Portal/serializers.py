from rest_framework import serializers
from .models import Application, AccessRequest, WorkflowHistory


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
