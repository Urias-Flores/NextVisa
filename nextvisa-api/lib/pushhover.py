import requests
from services.configuration_services import get_configuration
from models.configuration import ConfigurationResponse
import logging

logger = logging.getLogger(__name__)

class PushHover:
    def __init__(self):
        self.push_url = "https://api.pushover.net/1/messages.json"

    def _get_push_configuration(self):
        config: ConfigurationResponse = get_configuration()
        return config.push_token, config.push_user

    def send_message(self, msg):
        token, user = self._get_push_configuration()
        data = {
            "token": token,
            "user": user,
            "message": msg
        }

        try:
            requests.post(self.push_url, data)
        except Exception() as ex:
            logger.error("Error sending push notification", ex)
            pass