import time

class RateLimiter:
    """
    chat_id => [last_send_time, last_minute_time, msg_count]
    """
    def __init__(self):
        self.users = {}

    """
    less than 1 message per second;
    less than 20 message per minute(looks like group limitations but anyway)
    """
    def can_send_to(self, chat_id):
        now = time.time()
        if not chat_id in self.users:
            self.users[chat_id] = [now, now, 0]
            return True

        # 1 message per second case
        diff = now - self.users[chat_id][0]
        if diff <= 1:
            return False
        self.users[chat_id][0] = now

        # 20 messages per minute case
        diff = now - self.users[chat_id][1]
        if diff <= 60:
            msg_count = self.users[chat_id][2]
            if msg_count < 20:
                return True
            else:
                return False
        else:
            self.users[chat_id][1] = now
            self.users[chat_id][2] = 0
            return True

    def send_to(self, chat_id):
        if not chat_id in self.users:
            raise Exception("invalid usage of rate limiter")
        self.users[chat_id][2] += 1
