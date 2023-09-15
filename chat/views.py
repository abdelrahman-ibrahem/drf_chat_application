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
from chat.utils.generic import total_count_unread_messages, \
      get_unread_count_messages_for_chatroom, get_unread_count_messages_group_for_chatroom, read_messages


class ListChatrooms(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        chatrooms = ChatRoom.objects.all().order_by('-last_message_date')
        response = []
        # chatrooms_data = ChatroomSerializers(chatrooms, many=True).data
        user = self.request.user
        unread_messages = Message.objects.filter(is_read=False)
        total_unread_message = unread_messages.count()

        for chatroom in chatrooms:
            response.append({
                **ChatRoomSerializer(chatroom).data,
                'unread_count': get_unread_count_messages_for_chatroom(chatroom, user) \
                    if chatroom.type == ChatroomType.SELF else get_unread_count_messages_group_for_chatroom(chatroom, user)
            })
        
        return Response({
            "total_unread_messages": total_unread_message,
            'chatrooms_details': response
        }, status=status.HTTP_200_OK)



class RetreiveChatroom(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
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
        user = self.request.user
        chatroom_id = self.kwargs['chatroom_id']
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        messages = Message.objects.filter(chatroom=chatroom)
        messages = messages.all().order_by('-created_at')

        # read messages
        if messages.count() > 0:
            read_messages(chatroom, user)
            return messages
        else:
            return []

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


class CreateSingleChatroom(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            sender = self.request.user 
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

            return Response({
                'chatroom_id': chatroom.id,
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
