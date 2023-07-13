from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=240)
    members = models.ManyToManyField(User, related_name='chatroom_members')
    online_users = models.ManyToManyField(User, related_name='chatroom_online_users')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    chatroom = models.ForeignKey(ChatRoom, related_name='chatroom', on_delete=models.CASCADE, null=True, blank=True)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

