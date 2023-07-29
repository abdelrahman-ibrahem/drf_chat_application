from django.urls import path
from users.views import register_user, login_user

urlpatterns = [
    # Other URL patterns
    path('auth/register/', register_user, name='register_user'),
    path('auth/login/', login_user, name='login_user'),
]
