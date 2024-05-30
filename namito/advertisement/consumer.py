import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()
        logger.info("WebSocket connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        logger.info("WebSocket disconnected")

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        notification = event['notification']
        logger.info("Received notification event.")
        logger.info(f"Notification data: {notification}")
        logger.info(f"Sending notification: {notification}")
        await self.send(text_data=json.dumps(notification))

