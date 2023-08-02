from django.urls import path 
from chat import views


urlpatterns = [
    path('chat/', views.ListChatrooms.as_view()),
    path('chat/create.', views.CreateChatroomView.as_view()),
    path('chat/<int:chat_room_id>/', views.RetreiveChatroom.as_view()),
    path('chat/<int:chat_room_id>/messages/', views.RetreiveRoomMessages.as_view()),
    path('chat/<int:chatroom_id>/join/', views.AddMemberToChatroom.as_view()),
    path('chat/create-single-chatroom/', views.CreateSingleChatroom.as_view()),
    path('chat/send-image/', views.SendChatroomImage.as_view()),
    path('chat/<int:chatroom_id>/list-members/', views.ListChatroomMembers.as_view()),
    path('chat/<int:chatroom_id>/delete-members/', views.DeleteChatroomMembers.as_view()),

]