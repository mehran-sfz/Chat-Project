from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from user_conversations.models import Chat

from user_conversations.serializers import ChatSerializer, MessageSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatListView(APIView):
    """List all chats of the authenticated user"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        phone_number = request.query_params.get('phone_number')
        username = request.query_params.get('username')
        order_by = '-created_at' if request.query_params.get('order_by', 'newest') == 'oldest' else 'created_at'
        
        # Start with a base query of the user's chats
        chats = Chat.objects.filter(participants=request.user)

        # Apply filters for phone number or username, if provided
        if phone_number:
            chats = chats.filter(participants__phone_number=phone_number)
        elif username:
            chats = chats.filter(participants__profile__username=username)

        # Order by the specified direction
        chats = chats.order_by(order_by)
                
        
        serializer = ChatSerializer(chats, many=True)
        if serializer.data:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No chats found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """Create a new chat"""
        participant_phone_number = request.data.get('participant_phone_number')
        participant_username = request.data.get('participant_username')

        if not participant_phone_number and not participant_username:
            return Response({"error": "Participant phone number or username is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the participant exists based on phone number or profile's username
        participant = None
        if participant_phone_number:
            # search by phone number
            participant = User.objects.filter(
                phone_number=participant_phone_number).first()
        elif participant_username:
            # search by username
            participant = User.objects.filter(
                profile__username=participant_username).first()

        if not participant:
            return Response({"error": "Invalid participant"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the chat already exists
        chat = Chat.objects.filter(participants=request.user).filter(
            participants=participant).first()
        if chat:
            return Response({"error": "Chat already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # create a new chat
        chat = Chat.objects.create()
        chat.participants.add(request.user, participant)
        chat.save()

        return Response(ChatSerializer(chat).data, status=status.HTTP_201_CREATED)


class ChatDetailView(APIView):
    """Retrieve a chat and its messages"""

    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):

        try:
            chat = Chat.objects.get(id=chat_id)
        except Chat.DoesNotExist:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)

        if request.user not in chat.participants.all():
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageListView(APIView):
    """List all messages of a chat"""

    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        
        word_search = request.query_params.get('word_search')
        order_by = 'sended_at' if request.query_params.get('order_by') == 'oldest' else '-sended_at'
        limit = request.query_params.get('limit', 10)
        
        if not chat_id:
            return Response({"error": "Chat id is required"}, status=status.HTTP_400_BAD_REQUEST)
           
        # check it the user is part of the chat or not     
        chat = Chat.objects.filter(id=chat_id, participants=request.user).first()
        if not chat:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)

        # update all unread messages to read
        chat.messages.filter(status=False).exclude(sender=request.user).update(status=True)
        
        messages = chat.messages.all()
        if word_search:
            messages = messages.filter(content__icontains=word_search)
            
        # ordering and limiting the messages
        messages = messages.order_by(order_by)
        try:
            limit = int(limit)
            messages = messages[:limit]
        except:
            pass
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageCreateView(APIView):
    """Create a new message"""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, chat_id):

        chat = Chat.objects.filter(
            id=chat_id, participants=request.user).first()
        if not chat:
            return Response({"error": "Chat not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = MessageSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(conversation=chat, sender=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

