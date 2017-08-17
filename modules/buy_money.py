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
	bot.handlers["buy-money/confirm"] = confirm


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
		bot.call_handler("buy-money/start", message)
		return


	tx = {"rub": rub,
		  "btc": btc,
		  "uid": message.u_id}

	bot.user_set(message.u_id, "buy-btc:tx", tx)

def get_username(bot, message):
	tx = bot.user_get(message.u_id, "buy-btc:tx")

	confirm_message = bot.render_message("pending-payment", btc=tx["btc"], rub=tx["rub"])
	card_number_message = bot.render_message("card-number", number=main_wallet.card_number)
	tx_creating_error_message = bot.render_message("tx-creating-error")
	confirm_keyboard = bot.get_keyboard("confirm-purchase")

	username = message.text

	
	tx["username"] = username
	
	tx_id = main_wallet.add_tx(tx["username"], tx["id"], tx["btc"], tx["rub"])
	bot.user_delete(message.u_id, "buy-btc:tx")

	if tx_id == -1:
		bot.telegram.send_message(tx_creating_error_message, parse_mode="Markdown")
		bot.call_handler("main-menu", message)
		return

	bot.user_set(message.u_id, "buy-btc:tx-id", tx_id)	

	bot.telegram.send_message(confirm_message, parse_mode="Markdown", reply_markup=confirm_keyboard)
	bot.telegram.send_message(card_number_message, parse_mode="Markdown", reply_markup=confirm_keyboard)
	bot.set_next_handler("buy-money/confirm")	


def confirm(bot, message):
	cancelled_message = bot.render_message("tx-cancelled")
	wait_message = bot.render_message("wait-accepting")

	menu_keyboard = bot.get_keyboard("menu-keyboard")
	
	if bot.get_key("confirm-purchase", message.text) == "yes":
		bot.telegram.send_message(message.u_id, wait_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
	else:
		bot.telegram.send_message(message.u_id, cancelled_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
	
	

def admin_accept(bot, message):
	pass