"""
WebSocket routing for Django Channels.
"""
from django.urls import path
from security.consumers import AlertConsumer

websocket_urlpatterns = [
    path('ws/alerts/', AlertConsumer.as_asgi()),
]
