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

	bot.callback_handlers["admin-confirm-tx"] = admin_confirm
	bot.callback_handlers["admin-not-confirm-tx"] = admin_not_confirm

def start(bot, message):
	get_value_message = bot.render_message("get-value-to-buy", currency=main_wallet.get_currency())
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")

	bot.telegram.send_message(message.u_id, get_value_message, parse_mode="Markdown", reply_markup=back_to_menu_keyboard)
	bot.set_next_handler(message.u_id, "buy-money/get-value")

def get_value(bot, message):
	incorrect_value_message = bot.render_message("incorrect-value-to-buy")
	get_username_message = bot.render_message("get-username-to-buy")
	back_to_menu_keyboard = bot.get_keyboard("back-to-menu")


	message.text = message.text.upper()
	serach_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1}).*(?P<currency>(BTC|RUB))", message.text)
	if serach_result:
		value, currency = float(serach_result.group("value")), serach_result.group("currency")
		if currency == "RUB":
			rub = value
			btc = value/(main_wallet.get_currency() * 1.1)
		else:
			btc = value
			rub = value*(main_wallet.get_currency() * 1.1)


		tx = {"rub_value": rub,
			  "btc_value": btc,
			  "uid": message.u_id}

		bot.user_set(message.u_id, "buy-btc:tx", tx)

		bot.telegram.send_message(message.u_id, get_username_message, parse_mode="Markdown", reply_markup=back_to_menu_keyboard)
		bot.set_next_handler(message.u_id, "buy-money/get-username")		
	else:
		bot.telegram.send_message(message.u_id, incorrect_value_message, parse_mode="Markdown", reply_markup=back_to_menu_keyboard)
		bot.call_handler("buy-money/start", message)
		return

def get_username(bot, message):
	tx = bot.user_get(message.u_id, "buy-btc:tx")

	confirm_message = bot.render_message("pending-payment", btc=tx["btc_value"], rub=tx["rub_value"])
	card_number_message = bot.render_message("card-number", cards=main_wallet.cards)

	tx_creating_error_message = bot.render_message("tx-creating-error")
	confirm_keyboard = bot.get_keyboard("confirm-purchase")

	if not message.forward:
		username = message.text
		tx["username"] = username
		
		tx_id = main_wallet.add_tx(tx["username"], tx["uid"], tx["btc_value"], tx["rub_value"])
		bot.user_delete(message.u_id, "buy-btc:tx")

		if tx_id == -1:
			bot.telegram.send_message(message.u_id, tx_creating_error_message, parse_mode="Markdown")
			bot.call_handler("main-menu", message)
			return

		bot.user_set(message.u_id, "buy-btc:tx-id", tx_id)	

	bot.telegram.send_message(message.u_id, confirm_message, parse_mode="Markdown", reply_markup=confirm_keyboard)
	bot.telegram.send_message(message.u_id, card_number_message, parse_mode="Markdown", reply_markup=confirm_keyboard)

	bot.set_next_handler(message.u_id, "buy-money/confirm")	

def confirm(bot, message):
	cancelled_message = bot.render_message("tx-cancelled")
	wait_message = bot.render_message("wait-accepting")
	old_tx_message = bot.render_message("old-tx")

	if message.u_id != bot.admin:
		menu_keyboard = bot.get_keyboard("menu-keyboard")
	else:
		menu_keyboard = bot.get_keyboard("admin-menu-keyboard")

	tx_id = bot.user_get(message.u_id, "buy-btc:tx-id")
	
	tx = main_wallet.get_tx(tx_id)
	if not tx:
		bot.telegram.send_message(message.u_id, old_tx_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
		return

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

	bot.telegram.send_message(bot.admin, tx_info_message, parse_mode="Markdown", reply_markup=tx_confirm_keyboard)


def admin_confirm(bot, query):
	tx_id = query.data.split("/")[1]
	tx = main_wallet.get_tx(tx_id)

	tx_confirmed_message = bot.render_message("tx-confirmed")
	
	menu_keyboard = bot.get_keyboard("menu-keyboard")
	
	tx_info_message = bot.render_message("tx-info-for-admin", tx=tx, state=1)
	
	main_wallet.confirm_tx(tx_id)
	bot.telegram.send_message(tx["uid"], tx_confirmed_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
	bot.telegram.edit_message_text(chat_id=query.u_id,  
								   message_id=query.message.message_id, 
								   text=tx_info_message,
								   parse_mode="Markdown")

def admin_not_confirm(bot, query):
	tx_id = query.data.split("/")[1]
	tx = main_wallet.get_tx(tx_id)

	tx_not_confirmed_message = bot.render_message("tx-not-confirmed")

	
	menu_keyboard = bot.get_keyboard("menu-keyboard")

	tx_info_message = bot.render_message("tx-info-for-admin", tx=tx, state=2)
	
	main_wallet.not_confirm_tx(tx_id)
	bot.telegram.send_message(tx["uid"], tx_not_confirmed_message, parse_mode="Markdown",  reply_markup=menu_keyboard)
	bot.telegram.edit_message_text(chat_id=query.u_id,  
								   message_id=query.message.message_id, 
								   text=tx_info_message,
								   parse_mode="Markdown")