import os
import http.client
import urllib

LOG_IDENTIFIER = "[PUSHOVER]"


class PushOver:
    """General Class for sending messages through push over"""

    def __init__(self):
        """Requires environment varaibles set to work correctly"""
        self.GLOBAL_TOKEN: str = os.getenv("PSHOVR_LIMITSAPI")
        self.KEY: str = os.getenv("PSHOVR_USERKEY")

        if not self.GLOBAL_TOKEN or not self.KEY:
            raise ValueError(
                "Pushover token or user key is not set in environment variables."
            )

    def send(self, message: str):

        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(
                {
                    "token": self.GLOBAL_TOKEN,
                    "user": self.KEY,
                    "message": message,
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )

        response = conn.getresponse()

        if response.status != 200:
            print(
                f"{LOG_IDENTIFIER} Error: {response.status} - {response.read().decode()}"
            )
        else:
            print(f"{LOG_IDENTIFIER} Message sent successfully.")


if __name__ == "__main__":
    p = PushOver()
    p.send("Test message")
