class RateLimiter:
	new_dict = {chat_id: last_check_time}

	def can_send_to(chat_id):
		if chat_id in new_dict:
			diff = now - new_dict[chat_id].last_check_time
  			new_dict[chat_id].last_check_time = now
  			if diff < 1:
  				return True
			else:
  				new_dict[chat_id] = now
  				return True
			return False
