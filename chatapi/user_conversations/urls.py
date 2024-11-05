from django.urls import path
import user_conversations.views as views


urlpatterns = [
    path('chats/', views.ChatListView.as_view(), name='chats'),
    path('chats/<int:chat_id>/', views.ChatDetailView.as_view(), name='chat_detail'),
    path('chats/<int:chat_id>/messages/', views.MessageListView.as_view(), name='messages'),
    path('chats/<int:chat_id>/send/', views.MessageCreateView.as_view(), name='send_message'),
]


