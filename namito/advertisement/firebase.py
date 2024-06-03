import firebase_admin
from firebase_admin import credentials, messaging
import logging

logger = logging.getLogger(__name__)

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)


def send_firebase_notification(user, title, description, image_url=None):
    if not user.receive_notifications:
        logger.info(f"User {user} has disabled notifications.")
        return

    if not user.fcm_token:
        logger.warning(f"User {user} does not have FCM token. Skipping notification.")
        return

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
