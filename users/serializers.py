from rest_framework import serializers
from django.contrib.auth.models import User
from chat.models import ChatRoom

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'],
            validated_data['email'],
            validated_data['password']
        )
        chatroom = ChatRoom.objects.create(name=user.username)
        chatroom.members.add(user.id)
        chatroom.save()
        return user


class LoginSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

