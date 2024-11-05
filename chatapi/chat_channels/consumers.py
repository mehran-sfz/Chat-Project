# conversations/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from user_conversations.models import Chat, Message
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
import logging

logger = logging.getLogger(__name__)

User = get_user_model()
       
class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.chat_uuid = self.scope['url_route']['kwargs']['chat_uuid']
        self.room_group_name = f'chat_{self.chat_uuid}'

        # Check user authentication
        if self.scope["user"].is_anonymous:
            logger.warning("Anonymous user attempted to connect.")
            await self.close()
            return

        try:
            # Fetch the chat object from the database
            self.conversation = await self.get_chat()

            # Check if the user is a participant in the chat
            if self.scope["user"] not in await self.get_chat_participants(self.conversation):
                logger.warning(f"User {self.scope['user']} is not a participant in chat {self.chat_uuid}.")
                await self.close()
                return

            # Join the group if the user is a participant
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            logger.info(f"User {self.scope['user']} connected to chat {self.chat_uuid}.")
        except Chat.DoesNotExist:
            logger.error(f"Chat with id {self.chat_uuid} does not exist.")
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data.get('message')
        sender = self.scope["user"]
        reply_to = data.get('reply_to', None)

        if message_content:
            # Save message to the database
            await self.create_message(message_content, reply_to)


            message_payload = {
                'type': 'chat_message',
                'message': message_content,
                'sender': await self.get_sender_info(sender),
            }
            if reply_to:
                message_payload['reply_to'] = reply_to

            # Send the message to all users in the group
            await self.channel_layer.group_send(
                self.room_group_name,
                message_payload,
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
        }))

    @database_sync_to_async
    def get_chat(self):
        return Chat.objects.get(uuid=self.chat_uuid)

    @database_sync_to_async
    def get_chat_participants(self, chat):
        return list(chat.participants.all())

    @database_sync_to_async
    def create_message(self, content, reply_to):
        try:
            # check reply to message is exist in this chat
            reply_to_message = None
            if reply_to:
                reply_to_message = Message.objects.filter(conversation=self.conversation, id=reply_to).first()
                if not reply_to_message:
                    logger.error(f"Reply to message {reply_to} does not exist in chat {self.chat_uuid}.")
                    return
                
            message = Message.objects.create(conversation=self.conversation, sender=self.scope["user"], content=content, reply_to=reply_to_message)
            logger.info(f"Message created successfully: {message}")
            return message
        except Exception as e:
            logger.error(f"Error saving message: {e}")
        
    @database_sync_to_async
    def get_sender_info(self, user):
        
        if user.profile.username:
            return user.profile.username
        else:
            return user.phone_number