
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .models import Ticket, Message


@database_sync_to_async
def can_access_ticket(user, ticket_id):
    if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return False

    if user.is_superuser or getattr(user, "role", "") == "ADMIN":
        return True

    if ticket.created_by_id == user.id:
        return True

    return (
        getattr(user, "role", "") == "AGENT"
        and ticket.assigned_to_id == user.id
    )


@database_sync_to_async
def save_ticket_message(user, ticket_id, content):
    ticket = Ticket.objects.get(id=ticket_id)

    if ticket.status == Ticket.Status.CLOSED:
        raise ValueError("This ticket is closed.")

    message = Message.objects.create(
        ticket=ticket,
        sender=user,
        content=content,
    )

    return {
        "id": message.id,
        "ticket": ticket.id,
        "sender": user.username,
        "content": message.content,
        "created_at": message.created_at.isoformat(),
    }


class TicketConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.user = self.scope.get("user", AnonymousUser())
        self.ticket_id = int(
            self.scope["url_route"]["kwargs"]["ticket_id"]
        )
        self.group_name = f"ticket_{self.ticket_id}"

        allowed = await can_access_ticket(
            self.user, self.ticket_id
        )

        if not allowed:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name, self.channel_name
            )

    async def receive_json(self, content, **kwargs):
        event_type = content.get("type")

        if event_type == "message":
            message_text = content.get("content", "").strip()

            if not message_text or len(message_text) > 5000:
                await self.send_json({
                    "type": "error",
                    "message": "Message must contain 1–5000 characters.",
                })
                return

            try:
                message = await save_ticket_message(
                    self.user, self.ticket_id, message_text
                )
            except ValueError as exc:
                await self.send_json({
                    "type": "error",
                    "message": str(exc),
                })
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "chat_message",
                    "message": message,
                },
            )

        elif event_type == "typing":
            await self.channel_layer.group_send(
                self.group_name,
                {
                    "type": "typing_event",
                    "username": self.user.username,
                    "is_typing": bool(content.get("is_typing", True)),
                },
            )

    async def chat_message(self, event):
        await self.send_json({
            "type": "message",
            "message": event["message"],
        })

    async def typing_event(self, event):
        await self.send_json({
            "type": "typing",
            "username": event["username"],
            "is_typing": event["is_typing"],
        })
