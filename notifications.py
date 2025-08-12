import os
import urllib
import http.client
from dotenv import dotenv_values

class notificationsClass:

    config = dotenv_values(".env")
    pushover_token = config.get("PUSHOVER_TOKEN", os.getenv("PUSHOVER_TOKEN"))
    url = "api.pushover.net:443"

    def __init__(self):
        self.conn = http.client.HTTPSConnection(self.url)
        self.notification_list = list()
    
    def add_to_notifications(self, *args: str):
        self.notification_list.append(tuple(args))

    def send_notifications(self):

        responses = []
        chunk_size = 10

        try:

            # split to max 10 chunks (one message is 1000chars max)
            for i in range(0, len(self.notification_list), chunk_size):
                chunk = self.notification_list[i:i + chunk_size]
                msg = self._tuples_to_multiline_string(chunk)

                self.conn.request("POST", "/1/messages.json",
                urllib.parse.urlencode({
                    "user": "udyp91525b5c7hiubmfzh1i9r1wv8o",
                    "token": self.pushover_token,
                    "device": "peetphone",
                    "message": msg,
                    
                }), { "Content-type": "application/x-www-form-urlencoded" })
                response = self.conn.getresponse()
                responses.append(response)
                response.read()  # need to make sure the response is fully read
                self.conn.close()
        except Exception as e:
            print(f"Unexpected error: {e}")
        return responses

    def _tuples_to_multiline_string(self, tuples_list):
        txt = ""

        for tl in tuples_list:
            tls = [str(t) for t in tl]
            # every tuple (symbol, drop, etc) is first converted to a string like symbol|drop|etc, and a newline is added.
            # then this line-string is concatenated to one, which will be returned
            txt += ' | '.join(tls) + '\n'

        return txt


    def show_notification_list(self):
        return self.notification_list