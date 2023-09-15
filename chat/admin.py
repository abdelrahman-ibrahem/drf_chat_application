from django.contrib import admin
from chat.models import ChatRoom, Message, UnreadMessage

class ChatMessageInline(admin.TabularInline):
    model = Message

class UnreadMessageInline(admin.TabularInline):
    model = UnreadMessage

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
        ChatMessageInline,
        UnreadMessageInline
    ]

admin.site.register(Message)
admin.site.register(ChatRoom, ChatroomAdminView)
admin.site.register(UnreadMessage)
