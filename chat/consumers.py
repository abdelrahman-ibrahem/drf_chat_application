import json
from asgiref.sync import sync_to_async
from rest_framework.authtoken.models import Token 
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message, ChatRoom
from chat.utils.objects import ChatroomType, MessageType
from chat.serializers import MessageSerializer


@sync_to_async
def add_user_to_conversation(user, chatroom):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom)
        chatroom.online_users.add(user)
        chatroom.save()
    except ChatRoom.DoesNotExist:
        return None


@sync_to_async
def delete_user_to_conversation(user, chatroom):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom)
        chatroom.online_users.remove(user)
        chatroom.save()
    except ChatRoom.DoesNotExist:
        return None

@sync_to_async
def save_message(chatroom, message, message_type, sender,receiver=None):
    chatroom = ChatRoom.objects.get(id=chatroom)
    if receiver:
        if message_type == MessageType.TEXT:
            message = Message.objects.create(sender=sender, chatroom=chatroom, content=message, type=MessageType.TEXT, receiver=receiver)
    else:
        if message_type == MessageType.TEXT:
            message = Message.objects.create(sender=sender, chatroom=chatroom, type=MessageType.TEXT, content=message)
    
    if message_type == MessageType.TEXT:
        return message
    
@sync_to_async
def last_50_message(chatroom):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom)
        messages = chatroom.messages.all().order_by("-created_at")[:50]
        message_count = chatroom.messages.all().count()
        if message_count > 0:
            messages_data = MessageSerializer(messages, many=True).data
            return messages_data, message_count
        else:
            return {}, 0
    except ChatRoom.DoesNotExist:
        return None, None


@sync_to_async
def async_reading_message(chatroom_id, user):
    chatroom = ChatRoom.objects.get(id=chatroom_id)
    if chatroom.type == ChatroomType.SELF:
        messages = Message.objects.filter(receiver=user, chatroom=chatroom)
        for message in messages:
            message.is_read = True
            message.save()
    else:
        unread_messages = Message.objects.filter(is_read=False, chatroom=chatroom)
        for message in unread_messages:
            message.is_read = message.chatroom.online_users.filter(id=user.id).exists()
            message.save()

@sync_to_async
def get_chatroom_members(chatroom_id):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        members = []
        for member in chatroom.members.all():
            members.append({
                'id': member.id,
                "username":member.username,
                "email":member.email,
            })
        return members
    except ChatRoom.DoesNotExist:
        return []



@sync_to_async
def get_user(token):
    return Token.objects.get(key=token).user

@sync_to_async
def get_receiver(receiver_id):
    try:
        return User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return None

@sync_to_async
def get_receiver_from_chatroom(chatroom):
    try:
        return ChatRoom.objects.get(id=chatroom).owner
    except ChatRoom.DoesNotExist:
        return None

@sync_to_async
def get_all_online_users(chatroom):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom)
        # online_users = [user.username for user in chatroom.online_users.all()]
        online_users = []
        for user in chatroom.online_users.all():
            online_users.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
            })
        online_users_count = chatroom.get_online_users_count()
        return online_users, online_users_count
    except ChatRoom.DoesNotExist:
        return None, None

@sync_to_async
def get_chatroom(chatroom_id):
    try:
        return ChatRoom.objects.get(id=chatroom_id)
    except ChatRoom.DoesNotExist:
        return None

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # self.user = self.scope["user"]

        self.user = self.scope['user']
        # print(self.user)
        self.room_id = self.scope['url_route']['kwargs']['chat_room_id']
        # print(self.room_id)
        self.room_group_name = 'chatroom_%s' % self.room_id
        self.chatroom = await get_chatroom(self.room_id)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await add_user_to_conversation(self.user, self.room_id)

        # send all online users 
        online_users, online_users_count = await get_all_online_users(self.room_id)
        await self.send(text_data=json.dumps({
            "type": "online_users",
            'users': online_users,
            'count': online_users_count
        }))

        messages, messages_count = await last_50_message(self.room_id)
        await self.send(text_data=json.dumps({
                "type": "last_50_messages",
                "messages": messages,
                "has_more": messages_count,
            }))
        
        chatroom_members = await get_chatroom_members(self.room_id)
        await self.send(text_data=json.dumps({
            'type': 'chatroom_members',
            'members': chatroom_members
        }))

    

    async def disconnect(self, code):
        # Leave group
        await delete_user_to_conversation(self.user, self.room_id)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        date = text_data_json['date']
        message_type = text_data_json['type']
        image_url = text_data_json['image_url']

        if self.chatroom.type == ChatroomType.SELF:
            receiver = await get_receiver_from_chatroom(self.room_id)
        
        # print(receiver)
        # date = text_data_json.get('date')
        sender = self.user
        if self.chatroom.type == ChatroomType.SELF:
            if sender is not None:
                if message_type == MessageType.TEXT:
                    created_message = await save_message(self.room_id, message, sender, MessageType.TEXT, receiver)
                    await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': message,
                                'date': created_message.created_at
                            }
                        )
                elif message_type == MessageType.IMAGE:
                    await save_message(self.room_id, image_url, sender, MessageType.TEXT, receiver)
                    await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'image_chat',
                                'image_url': image_url,
                                'date': date
                            }
                        )
                elif message_type == 'ReadReport':
                    await async_reading_message(self.room_id, sender)
        elif self.chatroom.type == ChatroomType.GROUP:
            if sender is not None:
                if message_type == MessageType.TEXT:
                    created_message = await save_message(self.room_id, message, sender, MessageType.TEXT)
                    await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'chat_message',
                                'message': message,
                                'date': created_message.created_at
                            }
                        )
                elif message_type == MessageType.IMAGE:
                    await save_message(self.room_id, image_url, sender, MessageType.TEXT)
                    await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                'type': 'image_chat',
                                'image_url': image_url,
                                'date': date
                            }
                        )
                elif message_type == 'ReadReport':
                    await async_reading_message(self.room_id, sender)
                
    async def chat_message(self, event):
        message = event['message']
        date = event['date']

        await self.send(text_data=json.dumps({
            'date': date,
            'message': message,
            'type': MessageType.TEXT
        }))
    
    async def image_chat(self, event):
        message = event['image_url']
        date = event['date']

        await self.send(text_data=json.dumps({
            'date': date,
            'message': message,
            'type': MessageType.IMAGE
        }))
