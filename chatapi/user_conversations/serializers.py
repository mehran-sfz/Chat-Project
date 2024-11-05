from rest_framework import serializers
from .models import Chat, Message
from accounts.models import Profile
from django.contrib.auth import get_user_model


User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name', 'avatar', 'username']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True) 

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'is_active', 'profile']
      
      
class ShortMessageSerializer(serializers.ModelSerializer):
    short_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'short_content']
        
    def get_short_content(self, obj):
        if obj.content:
            return obj.content[:10] + '...'
        return None
        
class MessageSerializer(serializers.ModelSerializer):
    reply_to = ShortMessageSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'file', 'sended_at', 'edited_at', 'reply_to', 'status']
        read_only_fields = ['sended_at', 'edited_at']
    
    def validate(self, data):
        
        content = data.get('content')
        file = data.get('file')
        
        if not content and not file:
            raise serializers.ValidationError("Message must have content or file")
        
        return data
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)
    

class ChatSerializer(serializers.ModelSerializer):
    """serialize chat model and its participants and recent messages"""
    
    participants = UserSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Chat
        fields = ['id', 'uuid', 'participants', 'status', 'created_at', 'last_message']
        read_only_fields = ['created_at']
        
    def get_last_message(self, obj):
        """get the last message of the chat if exists"""
        
        last_message = obj.messages.order_by('-sended_at').first()
        if last_message:
            return ShortMessageSerializer(last_message).data
        return None