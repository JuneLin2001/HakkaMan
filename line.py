import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)
from dotenv import load_dotenv

load_dotenv()


class LineBot:
    def __init__(self):
        self.token = os.getenv("CHANNEL_ACCESS_TOKEN")
        self.user_id = os.getenv("USER_ID")
        self.configuration = Configuration(access_token=self.token)

    def send_message(self, text):
        with ApiClient(self.configuration) as api_client:
            api = MessagingApi(api_client)
            api.push_message(
                PushMessageRequest(
                    to=self.user_id,
                    messages=[TextMessage(text=text)],
                )
            )
