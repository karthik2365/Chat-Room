# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # room_name from path: ws://.../ws/chat/<room>/
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Optionally enforce authentication
        # user = self.scope["user"]  # requires AuthMiddlewareStack
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Expect JSON:
        { "sender": <id>, "receiver": <id>, "ciphertext": "<base64>" }
        Save Message (ciphertext only) and broadcast to group.
        """
        if text_data is None:
            return
        try:
            data = json.loads(text_data)
        except Exception:
            return

        sender_id = data.get("sender")
        receiver_id = data.get("receiver")
        ciphertext = data.get("ciphertext")

        # minimal validation
        if not sender_id or not receiver_id or not ciphertext:
            return

        # persist message (sync DB via database_sync_to_async)
        await self._save_message(sender_id, receiver_id, ciphertext)

        # broadcast the same payload to group (other clients in same room)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": {"sender": sender_id, "receiver": receiver_id, "ciphertext": ciphertext}
            }
        )

    async def chat_message(self, event):
        # Called for messages sent to the group
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def _save_message(self, sender_id, receiver_id, ciphertext):
        # simple create; will raise if user IDs invalid
        Message.objects.create(sender_id=sender_id, receiver_id=receiver_id, ciphertext=ciphertext)