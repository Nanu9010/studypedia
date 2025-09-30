import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import social.routing  # Added
from messenger.routing import websocket_urlpatterns as messenger_ws
from videocall.routing import websocket_urlpatterns as videocall_ws
from notifications.routing import websocket_urlpatterns as notifications_ws

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studypedia.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(social.routing.websocket_urlpatterns + messenger_ws + videocall_ws + notifications_ws)
    ),
})