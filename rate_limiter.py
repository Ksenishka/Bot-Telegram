class RateLimiter:
    def __init__i(self):
        self.users = {}

    def can_send_to(self, chat_id):
        now = time.now()
        ret = True

        if chat_id in self.users:
            diff = now - self.users[chat_id]
            self.users[chat_id] = now
            if diff <= 1:
                ret = False
        else:
            self.users[chat_id] = now

        return ret
