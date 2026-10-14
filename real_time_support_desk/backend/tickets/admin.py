

# Register your models here.

from django.contrib import admin
from .models import Ticket, Message


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "created_by",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "priority")
    search_fields = ("title", "description")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "sender", "created_at")
    search_fields = ("content",)
