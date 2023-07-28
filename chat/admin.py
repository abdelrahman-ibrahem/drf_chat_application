from django.contrib import admin
from chat.models import ChatRoom, Message

class ChatMessageInline(admin.TabularInline):
    model = Message

class ChatroomAdminView(admin.ModelAdmin):
    list_display = [
        'name',
        'owner',
        'type',
        'last_message',
        'last_message_date',
        'created_at',
    ]
    inlines = [
        ChatMessageInline
    ]

admin.site.register(Message)
admin.site.register(ChatRoom, ChatroomAdminView)
