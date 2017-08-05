def init(bot):
	bot.handlers["send-money"] = start
	bot.handlers["get_address"] = get_address
	bot.handlers["get-btc"] = get_btc
	bot.handlers["accpet-sending"] = accept_sending

 
def start(bot, message):
	get_adsress_message = bot.render_message("get-address")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")
	bot.set_next_handler(message.u_id, "get_address")

	bot.telegram.send_message(message.u_id, get_adsress_message, reply_markup=back_to_menu_keyboard)

def get_address(bot, message):
	bot.user_set(message.u_id, "address-to-send", message.text)
	get_btc_message = bot.render_message("get-btc")

	bot.set_next_handler(message.u_id, "get-btc")
	bot.telegram.send_message(message.u_id, get_btc_message)

def get_btc(bot, message):
	bot.user_set(message.u_id, "btc-to-send", float(message.text) * 10**8)
	address = bot.user_get(message.u_id, "address-to-send")

	get_btc_message = bot.render_message("accept-sending", btc=message.text, address=address)
	accept_keyboard = bot.get_keyboard("warning-to-send")

	bot.set_next_handler(message.u_id, "accpet-sending")

	bot.telegram.send_message(message.u_id, get_btc_message, parse_mode="Markdown",  reply_markup=accept_keyboard)

def accept_sending(bot, message):
	keyboard = bot.get_keyboard("menu-keyboard")
	if bot.get_key("warning-to-send", message.text) == "yes":
		bot.telegram.send_message(message.u_id, "Мани отправлены", parse_mode="Markdown",  reply_markup=keyboard)		
	else:
		bot.call_handler("main-menu", message)
		return 