import re
import os

from wallet import Wallet
from main_wallet import MainWallet

main_wallet = None

def init(bot):
	global main_wallet
	
	bot.handlers["send-money/start"] = start
	bot.handlers["send-money/get-address"] = get_address
	bot.handlers["send-money/get-value"] = get_value
	bot.handlers["send-money/accpet-sending"] = accept_sending
	main_wallet = MainWallet(bot, os.environ.get("PRIVATE_KEY"))

 
def start(bot, message):
	get_address_message = bot.render_message("get-address-to-send")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")

	bot.set_next_handler(message.u_id, "send-money/get-address")

	bot.telegram.send_message(message.u_id, get_address_message, reply_markup=back_to_menu_keyboard, parse_mode="Markdown")

def get_address(bot, message):
	if message.u_id != bot.admin:
		wallet = Wallet(bot, message.u_id)
	else:
		wallet = main_wallet

	incorrect_address_message = bot.render_message("incorrect-address-to-send")
	get_value_message = bot.render_message("get-value-to-send", comission=wallet.comission/10**8)

	if not message.forward:
		if not re.search("[0-9|a-z|A-Z]{30,34}", message.text):
			bot.telegram.send_message(message.u_id, incorrect_address_message, parse_mode="Markdown")
			bot.call_handler("send-money", message)
			return		

		bot.user_set(message.u_id, "address-to-send", message.text)

	bot.set_next_handler(message.u_id, "send-money/get-value")
	bot.telegram.send_message(message.u_id, get_value_message, parse_mode="Markdown")

def get_value(bot, message):
	if message.u_id != bot.admin:
		wallet = Wallet(bot, message.u_id)
	else:
		wallet = main_wallet

	incorrect_value_message = bot.render_message("incorrect-value-to-send")

	search_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1})", message.text)
	
	if not search_result:
		bot.telegram.send_message(message.u_id, incorrect_value_message, parse_mode="Markdown")
		bot.call_handler("send-money/get-address", message)
		return


	btc_value = search_result.group("value").replace(",", ".")
	bot.user_set(message.u_id, "btc-to-send", float(btc_value) * 10**8)
	address = bot.user_get(message.u_id, "address-to-send")

	accept_sending_message = bot.render_message("accept-sending", btc=btc_value, address=address)
	accept_keyboard = bot.get_keyboard("accept")

	bot.set_next_handler(message.u_id, "send-money/accpet-sending")
	bot.telegram.send_message(message.u_id, accept_sending_message, parse_mode="Markdown",  reply_markup=accept_keyboard)

def accept_sending(bot, message):
	if message.u_id != bot.admin:
		wallet = Wallet(bot, message.u_id)
	else:
		wallet = main_wallet

	ready_send_message = bot.render_message("ready-send")
	no_funds_message = bot.render_message("no-funds-to-send")
	push_error_message = bot.render_message("push-error")

	address = bot.user_get(message.u_id, "address-to-send")
	btc_value = bot.user_get(message.u_id, "btc-to-send")

	keyboard = bot.get_keyboard("menu-keyboard")
	if bot.get_key("accept", message.text) == "yes":
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