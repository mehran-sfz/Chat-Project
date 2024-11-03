# conversations/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Chat, Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from .serializers import MessageSerializer, UserSerializer

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        # بررسی احراز هویت کاربر
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')
        sender = self.scope["user"]

        if message_content:
            # ذخیره پیام در پایگاه داده
            message = await self.create_message(sender, message_content)

            # ارسال پیام به همه کاربران در گروه
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_content,
                    'sender': sender.username,
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    @database_sync_to_async
    def create_message(self, sender, content):
        chat = Chat.objects.get(id=self.chat_id)
        return Message.objects.create(conversation=chat, sender=sender, content=content)
