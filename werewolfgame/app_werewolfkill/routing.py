# app_werewolfkill/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/userinfo/", consumers.Myconsumer.as_asgi()),
]
