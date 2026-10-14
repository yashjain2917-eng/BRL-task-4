
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Ticket
from .serializers import TicketSerializer


class TicketListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == "ADMIN":
            return Ticket.objects.all()

        if user.role == "AGENT":
            return Ticket.objects.filter(assigned_to=user)

        return Ticket.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == "ADMIN":
            return Ticket.objects.all()

        if user.role == "AGENT":
            return Ticket.objects.filter(assigned_to=user)

        return Ticket.objects.filter(created_by=user)

    def perform_update(self, serializer):
        user = self.request.user

        if user.role != "ADMIN" and not user.is_superuser:
            raise PermissionDenied(
                "Only administrators can update tickets through this endpoint."
            )

        serializer.save()

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import Ticket, Message
from .serializers import TicketSerializer, MessageSerializer

User = get_user_model()


class TicketAssignView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if not (request.user.is_superuser or request.user.role == "ADMIN"):
            raise PermissionDenied(
                "Only administrators can assign tickets."
            )

        ticket = get_object_or_404(Ticket, pk=pk)
        agent_id = request.data.get("agent_id")

        if not agent_id:
            raise ValidationError(
                {"agent_id": "This field is required."}
            )

        agent = get_object_or_404(User, pk=agent_id)

        if agent.role != "AGENT" or not agent.is_active:
            raise ValidationError(
                {"agent_id": "Select an active support agent."}
            )

        ticket.assigned_to = agent
        ticket.save(update_fields=["assigned_to", "updated_at"])

        return Response(
            TicketSerializer(ticket).data,
            status=status.HTTP_200_OK,
        )


class TicketStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        user = request.user

        if not (
            user.is_superuser
            or user.role in ["ADMIN", "AGENT"]
        ):
            raise PermissionDenied(
                "Only support agents or administrators can change ticket status."
            )

        ticket = get_object_or_404(Ticket, pk=pk)

        if not (
            user.is_superuser
            or user.role == "ADMIN"
            or ticket.assigned_to_id == user.id
        ):
            raise PermissionDenied(
                "You can only update tickets assigned to you."
            )

        new_status = request.data.get("status")
        valid_statuses = Ticket.Status.values

        if new_status not in valid_statuses:
            raise ValidationError({
                "status": f"Choose one of: {', '.join(valid_statuses)}"
            })

        ticket.status = new_status
        ticket.save(update_fields=["status", "updated_at"])

        return Response(TicketSerializer(ticket).data)


class TicketMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_ticket(self):
        user = self.request.user
        ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"])

        if user.is_superuser or user.role == "ADMIN":
            return ticket

        if ticket.created_by_id == user.id:
            return ticket

        if ticket.assigned_to_id == user.id and user.role == "AGENT":
            return ticket

        raise PermissionDenied(
            "You do not have permission to access this ticket."
        )

    def get_queryset(self):
        ticket = self.get_ticket()
        return Message.objects.filter(ticket=ticket).select_related("sender")

    def perform_create(self, serializer):
        ticket = self.get_ticket()

        if ticket.status == Ticket.Status.CLOSED:
            raise PermissionDenied(
                "Cannot send messages to a closed ticket."
            )

        serializer.save(
            ticket=ticket,
            sender=self.request.user,
        )
