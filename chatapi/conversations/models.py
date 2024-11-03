from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


User = get_user_model()

# Chat model
class Chat(models.Model):
    
    participants = models.ManyToManyField(User, related_name='chats')
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        participants = ', '.join([user.username for user in self.participants.all()])
        return f"Chat between {participants}"

class Message(models.Model):
    
    conversation = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    status = models.BooleanField(default=True)
    sended_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        
        if self.content and self.file:
            return f"{self.sender} sent a file and a message"
        elif self.content:
            return f"{self.sender} sent a message"
        else:
            return f"{self.sender} sent a file"
        
        
    def save(self, *args, **kwargs):
        if not self.content and not self.file:
            raise ValueError("Message need to have one of the content or file fields")
        