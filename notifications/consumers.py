import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Allow only authenticated users
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close(code=4001)
            return        
        
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"user_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        
    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "notification": event["notification"],
        }))