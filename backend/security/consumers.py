"""
WebSocket consumers for real-time alerts.
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class AlertConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time alert notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        user = self.scope['user']
        
        if not user.is_authenticated:
            await self.close()
            return
        
        # Join organization-specific room
        if user.organization:
            self.room_name = f'alerts_org_{user.organization.id}'
            self.room_group_name = f'alerts_org_{user.organization.id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"User {user.username} connected to alerts WebSocket")
        else:
            await self.close()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming messages (not used for alerts, but required)."""
        pass
    
    async def alert_message(self, event):
        """Receive message from room group and send to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': event['alert_type'],
            'severity': event['severity'],
            'message': event['message'],
            'data': event.get('data', {}),
            'timestamp': event.get('timestamp'),
        }))


def broadcast_alert(org_id, alert_data):
    """
    Broadcast alert to all connected clients in an organization.
    Can be called from Django views or Celery tasks.
    """
    channel_layer = get_channel_layer()
    room_group_name = f'alerts_org_{org_id}'
    
    from django.utils import timezone
    
    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'alert_message',
            'alert_type': alert_data.get('type', 'general'),
            'severity': alert_data.get('severity', 'medium'),
            'message': alert_data.get('message', ''),
            'data': alert_data.get('data', {}),
            'timestamp': timezone.now().isoformat(),
        }
    )
