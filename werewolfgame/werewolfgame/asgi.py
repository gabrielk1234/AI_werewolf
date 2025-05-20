# werewolfgame/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import werewolfgame.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'werewolfgame.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            werewolfgame.routing.websocket_urlpatterns
        )
    ),
})
