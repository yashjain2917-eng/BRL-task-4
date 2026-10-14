
from django.urls import path
from .views import TicketListCreateView, TicketDetailView

urlpatterns = [
    path("", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
]

from .views import (
    TicketListCreateView,
    TicketDetailView,
    TicketAssignView,
    TicketStatusView,
)

urlpatterns = [
    path("", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("<int:pk>/assign/", TicketAssignView.as_view(), name="ticket-assign"),
    path("<int:pk>/status/", TicketStatusView.as_view(), name="ticket-status"),
]

from django.urls import path
from .views import (
    TicketListCreateView,
    TicketDetailView,
    TicketAssignView,
    TicketStatusView,
    TicketMessageListCreateView,
)

urlpatterns = [
    path("", TicketListCreateView.as_view(), name="ticket-list-create"),
    path("<int:pk>/", TicketDetailView.as_view(), name="ticket-detail"),
    path("<int:pk>/assign/", TicketAssignView.as_view(), name="ticket-assign"),
    path("<int:pk>/status/", TicketStatusView.as_view(), name="ticket-status"),
    path(
        "<int:pk>/messages/",
        TicketMessageListCreateView.as_view(),
        name="ticket-messages",
    ),
]
