import re
import os

from main_wallet import MainWallet

main_wallet = None

def init(bot):
	global main_wallet
	main_wallet = MainWallet(bot, os.environ.get("PRIVATE_KEY"))

	bot.handlers["buy-money/start"] = start
	bot.handlers["buy-money/get-value"] = get_value
	bot.handlers["buy-money/get-username"] = get_username
	bot.handlers["buy-money/accept"] = accept


def start(bot, message):
	get_value_message = bot.render_message("get-value-to-buy")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")

	bot.telegram.send_message(get_value_message, reply_markup=back_to_menu_keyboard)
	bot.set_next_handler("buy-money/get-value")

def get_value(bot, message):
	incorrect_value_message = bot.render_message("incorrect-value-to-buy")
	get_username_message = bot.render_message("get-username-to-buy")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")

	serach_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1}).*(?P<corency>(BTC|RUB))", message.text)
	if serach_result:
		value, btc = serach_result.group("value"), serach_result.group("curency")
		if value == "RUB":
			rub = btc  
			btc = btc/main_wallet.get_curency()
		else:
			rub = btc*main_wallet.get_curency()
	
		bot.telegram.send_message(get_username_message, reply_markup=back_to_menu_keyboard)
		bot.set_next_handler("buy-money/get-username")		
	
	else:
		bot.telegram.send_message(incorrect_value_message, reply_markup=back_to_menu_keyboard)
		bot.call_handler("buy-money/get-value", message)
		return

def get_username(bot, message):
	accept_message = bot.render_message("accept-buy")
	accept_keyboard = bot.get_keyboard("accept")

	username = message.text

	bot.telegram.send_message(get_username_message, parse_mode="Markdown", reply_markup=accept_keyboard)
	bot.set_next_handler("buy-money/accept")	


def accept(bot, message):
	pass


def admin_accept(bot, message):
	pass