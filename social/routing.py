from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/social/$', consumers.SocialConsumer.as_asgi()),
]