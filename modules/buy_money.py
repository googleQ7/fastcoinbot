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


		tx = {"rub_value": rub,
			  "btc_value": btc,
			  "uid": message.u_id}

		bot.user_set(message.u_id, "buy-btc:tx", tx)

		bot.telegram.send_message(get_username_message, reply_markup=back_to_menu_keyboard)
		bot.set_next_handler("buy-money/get-username")		
	else:
		bot.telegram.send_message(incorrect_value_message, reply_markup=back_to_menu_keyboard)
		bot.call_handler("buy-money/start", message)
		return

def get_username(bot, message):
	tx = bot.user_get(message.u_id, "buy-btc:tx")

	confirm_message = bot.render_message("pending-payment", btc=tx["btc_value"], rub=tx["rub_value"])
	card_number_message = bot.render_message("card-number", number=main_wallet.card_number)
	tx_creating_error_message = bot.render_message("tx-creating-error")
	confirm_keyboard = bot.get_keyboard("confirm-purchase")

	if not message.forward:
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
	tx_id = bot.user_get(message.u_id, "buy-btc:tx-id")
	
	if bot.get_key("confirm-purchase", message.text) == "yes":
		bot.telegram.send_message(message.u_id, wait_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
		send_confirm_message_to_admin(bot, message, tx_id)
	elif bot.get_key("confirm-purchase", message.text) == "no":
		main_wallet.not_confirm_tx(tx_id)
		bot.user_delete(message.u_id, "buy-btc:tx-id")
		bot.telegram.send_message(message.u_id, cancelled_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
	else:
		bot.call_handler("buy-money/get-username", message)
		return	

def send_confirm_message_to_admin(bot, message, tx_id):
	tx = main_wallet.get_tx(tx_id)
	tx_info_message = bot.render_message("tx-info-for-admin", tx=tx)
	tx_confirm_keyboard = bot.get_inline_keyboard("confirm-tx", params={"tx-id":tx_id})

	bot.telegram.send_message(self.admin, tx_info_message, parse_mode="Markdown", reply_markup=tx_confirm_keyboard)


def admin_confirm(bot, query):
	tx_id = query.data.split("/")[1]
	tx_info_message = bot.render_message("tx-info-for-admin", tx=tx)
	
	main_wallet.confirm_tx(tx_id)
	bot.telegram.edit_message_text(chat_id=query.u_id,  
								   message_id=query.message.message_id, 
								   text=tx_info_message,
								   parse_mode="Markdown")

def admin_not_confirm(bot, query):
	tx_id = query.data.split("/")[1]
	tx_info_message = bot.render_message("tx-info-for-admin", tx=tx)
	
	main_wallet.not_confirm_tx(tx_id)
	bot.telegram.edit_message_text(chat_id=query.u_id,  
								   message_id=query.message.message_id, 
								   text=tx_info_message,
								   parse_mode="Markdown")

