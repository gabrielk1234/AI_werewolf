# app_werewolfkill/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/userinfo/", consumers.UserInfoConsumer.as_asgi()),
]
