from chat.models import ChatRoom, Message, UnreadMessage
from chat.utils.objects import ChatroomType
from django.db.models  import Q

def get_unread_count_messages_group(user):
    chatrooms = ChatRoom.objects.filter(type=ChatroomType.GROUP)
    total_unread = 0
    # sender_unread_count = 0
    for chatroom in chatrooms:
        # messages = Message.objects.filter(chatroom=chatroom, is_read=False)
        # total_unread += messages.count()
        # sender_unread_count += messages.filter(sender=user).count()
        total_unread += chatroom.chatroom_unread.filter(receiver=user, is_read=False).count()

    # result = total_unread - sender_unread_count
    return total_unread


def total_count_unread_messages(user):
    # unread_message_count =  Message.objects.filter(Q(receiver=user), is_read=False).count()
    # unread_count_group = get_unread_count_messages_group(user)
    # unread_all_chats_messages_count =  unread_message_count +  unread_count_group
    total_unread_count_messages = UnreadMessage.objects.filter(receiver=user, is_read=False).count()
    return total_unread_count_messages

def get_unread_count_messages_group_for_chatroom(chatroom, user):
    # messages = Message.objects.filter(chatroom=chatroom, is_read=False)
    # total_unread = messages.count()
    # sender_unread_count = messages.filter(sender=user).count()
    
    # result = total_unread - sender_unread_count
    result = chatroom.chatroom_unread.filter(receiver=user, is_read=False).count()
    return result


def get_unread_count_messages_for_chatroom(chatroom, user):
    if chatroom.type == ChatroomType.SELF:
        # unread_count = Message.objects.filter(receiver=user, chatroom=chatroom, is_read=False).count()
        unread_count = chatroom.chatroom_unread.filter(receiver=user, is_read=False).count()
    elif chatroom.type == ChatroomType.GROUP:
        unread_count = get_unread_count_messages_group_for_chatroom(chatroom, user)
    return unread_count


def read_messages(chatroom, user):
    unread_messages = chatroom.chatroom_unread.filter(receiver=user, is_read=False)
    for message in unread_messages:
        message.is_read = True
        message.save()