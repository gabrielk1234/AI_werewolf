# app_werewolfkill/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path("ws/userinfo/", consumers.Myconsumer.as_asgi()),
]
