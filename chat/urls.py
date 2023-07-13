from django.urls import path 
from . import views


urlpatterns = [
    path('chat/chatrooms/', views.ListChatrooms.as_view()),
    path('chat/chatrooms/<int:chat_room_id>/', views.RetreiveChatroom.as_view()),
    path('chat/<int:chat_room_id>/messages/', views.RetreiveRoomMessages.as_view()),
    path('chat/messages/create/', views.CreateRoomMessage.as_view()),
    path('chat/<int:chatroom_id>/join/', views.AddToChatroom.as_view())
]