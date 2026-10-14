
from rest_framework import serializers
from .models import Ticket, Message


class TicketSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(
        source="created_by.username"
    )
    assigned_to = serializers.ReadOnlyField(
        source="assigned_to.username"
    )

    class Meta:
        model = Ticket
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "assigned_to",
            "created_at",
            "updated_at",
        ]




from rest_framework import serializers
from .models import Message


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(
        source="sender.username"
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "ticket",
            "sender",
            "content",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "ticket",
            "sender",
            "created_at",
        ]
