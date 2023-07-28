from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from chat.models import ChatRoom, Message
from chat.serializers import ChatRoomSerializer, MessageSerializer
from chat.utils.objects import ChatroomType, MessageType

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

class CreateChatroomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            owner = self.request.user
            name = request.data.get('name')
            members = list(request.data.get('members'))
            chatroom = ChatRoom.objects.create(name=name, owner=owner)
            if members:
                for member in members:
                    user = User.objects.get(id=member)
                    chatroom.members.add(user)
            
            chatroom.save()
            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(status=status.HTTP_409_CONFLICT)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sender = self.request.user 
            message = request.data.get('message')
            receiver_id = request.data.get('receiver_id')
            receiver = User.objects.get(id=receiver_id)

            chatroom = ChatRoom.objects.create(
                owner=receiver,
                name=receiver.username,
                type=ChatroomType.SELF,
            )

            chatroom.members.add(sender)
            chatroom.members.add(receiver)
            chatroom.save()

            message = Message.objects.create(
                chatroom=chatroom,
                sender=sender,
                receiver=receiver,
                type=MessageType.TEXT,
                content=message
            )
            return Response({
                'content': str(message),
                'created_at' : message.created_at.strftime("%Y-%m-%d")
            }, status=status.HTTP_201_CREATED)

        except:
            return Response(status=status.HTTP_409_CONFLICT) 


class SendChatroomImage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            image = request.data['image']
            chatroom_id = request.data['chatroom_id']
            # save the class object
            user = request.user
            chatroom = ChatRoom.objects.get(pk=chatroom_id)
            
            chat_message = Message(chatroom=chatroom, image=image, type=MessageType.IMAGE, sender=user)
            chat_message.save()
            
            content = {
                'url': chat_message.image.url,
                'date': chat_message.created_at.strftime("%Y-%m-%d")
            }
            return Response(content, status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_409_CONFLICT)


class CreateRoomMessage(CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [
        IsAuthenticated
    ]

class AddMemberToChatroom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chatroom_id):
        try:
            try:
                chatroom = ChatRoom.objects.get(id=chatroom_id)
                if request.user == chatroom.owner:
                    members = list(request.data.get('members'))
                    for member in members:
                        if not chatroom.members.filter(id=int(member)).exists():
                            chatroom.members.add(member)
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            except ChatRoom.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response(status=status.HTTP_409_CONFLICT)


class ListChatroomMembers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chatroom_id):
        try:
            chatroom = ChatRoom.objects.get(id=chatroom_id)
            members = []
            for member in chatroom.members.all():
                members.append({
                    "id": member.id,
                    "username": member.username,
                    "email":member.email,
                })
            return Response(members, status=status.HTTP_200_OK)
        
        except ChatRoom.DoesNotExist:
            return Response(status=status.HTTP_409_CONFLICT)


class DeleteChatroomMembers(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, chatroom_id):
        members = request.data.get('members')
        # chatroom_id = self.kwargs['chatroom_id']
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        for member in members:
            if chatroom.members.filter(id=int(member)).exists():
                chatroom.members.remove(member)
        
        return Response(status=status.HTTP_200_OK)
