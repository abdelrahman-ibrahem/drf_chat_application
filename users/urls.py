from django.urls import path
from users.views import register_user, login_user

urlpatterns = [
    # Other URL patterns
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
]
