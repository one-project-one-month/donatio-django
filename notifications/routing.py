from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/notifications/<str:room_name>/", consumers.NotificationConsumer.as_asgi()),
]
