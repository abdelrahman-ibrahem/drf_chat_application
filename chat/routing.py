from django.urls import path
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chatrooms/<int:chat_room_id>/', ChatConsumer.as_asgi())
]