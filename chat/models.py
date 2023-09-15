from django.db import models
from django.contrib.auth.models import User
from chat.utils.objects import MessageType, ChatroomType


class ChatRoom(models.Model):
    name = models.CharField(
        max_length=240
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owner'
    )
    members = models.ManyToManyField(
        User,
        related_name='chatroom_members'
    )
    online_users = models.ManyToManyField(
        User,
        related_name='chatroom_online_users',
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=240,
        choices=ChatroomType.choices,
        default=ChatroomType.GROUP
    )
    
    last_message = models.TextField(
        null=True,
        blank=True
    )
    last_message_date = models.DateTimeField(
        auto_now_add=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chatroom_sender',
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chatroom_receiver',
        null=True,
        blank=True
    )

    def get_online_users_count(self):
        return self.online_users.count()

class Message(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom,
        related_name='messages',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    sender = models.ForeignKey(
        User,
        related_name='sender',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        related_name='receiver',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    content = models.TextField(
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to="chatrooms/images/",
        null=True,
        blank=True
    )
    type = models.CharField(
        max_length=240,
        choices=MessageType.choices,
        default=MessageType.TEXT,
    )
    is_read = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )


class UnreadMessage(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name='chatroom_unread'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='messafe_unread'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sender_unread',
        null=True,
        blank=True
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receiver_unread',
        null=True,
        blank=True
    )
    is_read = models.BooleanField(
        default=False
    )
    creation_date = models.DateTimeField(
        auto_now_add=True
    )