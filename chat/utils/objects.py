from django.db.models import TextChoices

class MessageType(TextChoices):
    IMAGE = 'I'
    TEXT = 'T'


class ChatroomType(TextChoices):
    SELF = 'S'
    GROUP = 'G'