import firebase_admin
from firebase_admin import credentials, messaging
import logging

logger = logging.getLogger(__name__)

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)


def send_firebase_notification(title, description, image_url=None, user=None):
    if user and user.fcm_token and user.receive_notifications:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=description,
                image=image_url,
            ),
            token=user.fcm_token,
        )
        try:
            response = messaging.send(message)
            logger.info(f"Successfully sent message: {response}")
            return response
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
