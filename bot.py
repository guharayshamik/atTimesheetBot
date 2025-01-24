class TelegramBot:
    def __init__(self, token):
        self.token = token

    def start(self):
        print(f"Starting bot with token: {self.token}")
