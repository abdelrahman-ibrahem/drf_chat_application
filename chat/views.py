from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message
from chat.serializers import ChatRoomSerializer, MessageSerializer

class ListChatrooms(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChatRoomSerializer
    queryset = ChatRoom.objects.all()



class RetreiveChatroom(RetrieveAPIView):
    # permission_classes = (IsAuthenticated,)
    serializer_class = ChatRoomSerializer
    queryset = ChatRoom.objects.all()
    lookup_field = 'chat_room_id'


    def get_queryset(self):
        try:
            qs = ChatRoom.objects.get(id=self.kwargs['chat_room_id'])
            
            return qs
        except ChatRoom.DoesNotExist:
            return None

class RetreiveRoomMessages(ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        chatroom_id = self.kwargs['chat_room_id']
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        qs = Message.objects.filter(
            sender=self.request.user,
            chatroom=chatroom
        )
        return qs


class CreateRoomMessage(CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [
        IsAuthenticated
    ]

class AddToChatroom(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            chatroom.members.add(self.request.user.id)
            chatroom.save()
            return Response({
                "message":"success",
            }, status=status.HTTP_200_OK)
        except ChatRoom.DoesNotExist:
            return Response({
                "message": "The chatroom is not found"
            })