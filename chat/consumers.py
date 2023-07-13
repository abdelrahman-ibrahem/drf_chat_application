import json
from asgiref.sync import sync_to_async
from rest_framework.authtoken.models import Token 
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from chat.models import Message, ChatRoom

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
def save_message(chatroom, message, sender, receiver):
    chatroom = ChatRoom.objects.get(id=chatroom)
    Message.objects.create(sender=sender, chatroom=chatroom, content=message, receiver=receiver)

@sync_to_async
def get_user(token):
    return Token.objects.get(key=token).user

@sync_to_async
def get_receiver(receiver_id):
    try:
        return User.objects.get(id=receiver_id)
    except User.DoesNotExist:
        return None



class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # self.user = self.scope["user"]

        self.user = self.scope['user']
        # print(self.user)
        self.room_id = self.scope['url_route']['kwargs']['chat_room_id']
        # print(self.room_id)
        self.room_group_name = 'chatroom_%s' % self.room_id
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await add_user_to_conversation(self.user, self.room_id)

    

    async def disconnect(self, code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await delete_user_to_conversation(self.user, self.room_id)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        receiver_id = text_data_json['receiver_id']
        receiver = await get_receiver(receiver_id)
        # print(receiver)
        # date = text_data_json.get('date')
        sender = self.user
        if sender is not None:
            await save_message(self.room_id, message, sender, receiver)
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'sender_id': sender.id,
                    }
                )
        
    async def chat_message(self, event):
        # message = event['message']
        # receiver_id = event['receiver_id']

        await self.send(text_data=json.dumps({
            # 'date': date,
            'message': event.get('message'),
            'receiver_id': event.get('receiver_id')
        }))
