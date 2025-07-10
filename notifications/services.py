from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .serializers import NotificationReadSerializer

def send_notification_to_user(notification):
    channel_layer = get_channel_layer()
    group_name = f"user_{notification.receiver_object_id}"  # Must match the consumer's group name
    
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",  # Must match the consumer method
            "notification": NotificationReadSerializer(notification),
        }
    )