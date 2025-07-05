import json
from channels.consumer import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # join the group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # leave the group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def save_message(self, sender_id, sender_type, room_name, message):
        from .models import Chat, ChatMessage
        from accounts.models import User
        from organizations.models import Organization
        from .constants import SenderType

        chat = await database_sync_to_async(Chat.objects.get)(id=room_name)

        if sender_type == SenderType.DONOR:
            donor = await database_sync_to_async(User.objects.get)(id=sender_id)
            organization = None
        else:
            organization = await database_sync_to_async(Organization.objects.get)(
                id=sender_id
            )
            donor = None

        await database_sync_to_async(ChatMessage.objects.create)(
            chat=chat,
            sender=sender_type,
            donor=donor,
            organization=organization,
            content=message,
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender_type = data["sender_type"]
        sender_id = data["sender_id"]

        await self.save_message(sender_id, sender_type, self.room_name, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "sender_type": sender_type,
                "sender_id": sender_id,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        sender_type = event["sender_type"]
        sender_id = event["sender_id"]

        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender_type": sender_type,
                    "sender_id": sender_id,
                    "timestamp": datetime.now(),
                }
            )
        )
