import firebase_admin
from firebase_admin import credentials, messaging
import logging

from namito.users.models import User

logger = logging.getLogger(__name__)

cred = credentials.Certificate('firebase_key.json')
firebase_admin.initialize_app(cred)


def send_firebase_notification(title, description, image_url=None, user_id=None):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.error(f"User with id {user_id} does not exist")
        return

    if user.fcm_token and user.receive_notifications:
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
