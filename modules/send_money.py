import re

from wallet import Wallet

def init(bot):
	bot.handlers["send-money"] = start
	bot.handlers["get-address"] = get_address
	bot.handlers["get-btc"] = get_btc
	bot.handlers["accpet-sending"] = accept_sending

 
def start(bot, message):
	get_address_message = bot.render_message("get-address")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")
	bot.set_next_handler(message.u_id, "get-address")

	bot.telegram.send_message(message.u_id, get_address_message, reply_markup=back_to_menu_keyboard, parse_mode="Markdown")

def get_address(bot, message):
	if not message.forward:
		incorrect_address_message = bot.render_message("incorrect-address")

		if not re.search("[0-9|a-z|A-Z]{30,34}", message.text):
			bot.telegram.send_message(message.u_id, incorrect_address_message, parse_mode="Markdown")
			bot.call_handler("send-money", message)
			return		

		bot.user_set(message.u_id, "address-to-send", message.text)
	get_btc_message = bot.render_message("get-btc")

	bot.set_next_handler(message.u_id, "get-btc")
	bot.telegram.send_message(message.u_id, get_btc_message, parse_mode="Markdown")

def get_btc(bot, message):
	search_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1})", message.text)
	incorrect_value_message = bot.render_message("incorrect-value")
	
	if not search_result:
		bot.telegram.send_message(message.u_id, incorrect_value_message, parse_mode="Markdown")
		bot.call_handler("get-address", message)
		return


	btc_value = search_result.group("value").replace(",", ".")
	bot.user_set(message.u_id, "btc-to-send", float(btc_value) * 10**8)
	address = bot.user_get(message.u_id, "address-to-send")

	accept_sending_message = bot.render_message("accept-sending", btc=btc_value, address=address)
	accept_keyboard = bot.get_keyboard("warning-to-send")

	bot.set_next_handler(message.u_id, "accpet-sending")

	bot.telegram.send_message(message.u_id, accept_sending_message, parse_mode="Markdown",  reply_markup=accept_keyboard)

def accept_sending(bot, message):
	wallet = Wallet(bot, message.u_id)

	address = bot.user_get(message.u_id, "address-to-send")
	btc_value = bot.user_get(message.u_id, "btc-to-send")

	ready_send_message = bot.render_message("ready-send")
	no_funds_message = bot.render_message("no-funds")
	push_error_message = bot.render_message("push-error")

	keyboard = bot.get_keyboard("menu-keyboard")
	if bot.get_key("warning-to-send", message.text) == "yes":
		code = wallet.send_money(btc_value, address)
		
		if code == 0:
			bot.telegram.send_message(message.u_id, ready_send_message, parse_mode="Markdown",  reply_markup=keyboard)		
		elif code == -1:
			bot.telegram.send_message(message.u_id, no_funds_message, parse_mode="Markdown",  reply_markup=keyboard)
		else:
			bot.telegram.send_message(message.u_id, push_error_message, parse_mode="Markdown",  reply_markup=keyboard)
	else:
		bot.call_handler("main-menu", message)
		return 