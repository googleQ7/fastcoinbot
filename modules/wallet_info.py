from wallet import Wallet
from main_wallet import MainWallet

import os

main_wallet = None

def init(bot):
	global main_wallet

	bot.handlers["wallet-info/start"] = start
	main_wallet = MainWallet(bot, os.environ.get("PRIVATE_KEY"))

def start(bot, message):
	if message.u_id != bot.admin:
		wallet = Wallet(bot, message.u_id)
	else:
		wallet = main_wallet

	if message.u_id != bot.admin:
		menu_keyboard = bot.get_keyboard("menu-keyboard")
	else:
		menu_keyboard = bot.get_keyboard("admin-menu-keyboard")
		
	balance = wallet.get_balance()/10**8
	curecy = wallet.get_currency() * balance
	
	info = bot.render_message("wallet-info", balance=wallet.get_balance()/10**8, rub=curecy)
	bot.telegram.send_message(message.u_id, info, reply_markup = menu_keyboard, parse_mode="Markdown")

