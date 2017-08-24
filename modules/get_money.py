from wallet import Wallet
from main_wallet import MainWallet

import qrcode
import io
import os

main_wallet = None

def init(bot):
	global main_wallet

	bot.handlers["get-money/start"] = start
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

	info = bot.render_message("get-money")
	btc_address = bot.render_message("btc-address", address=wallet.address)
	
	
	qr_image = qrcode.make(wallet.address)
	qr_bytes = io.BytesIO()
	qr_image.save(qr_bytes, format='PNG')
	
	qr_file = io.BytesIO(qr_bytes.getvalue())

	bot.telegram.send_message(message.u_id, info, reply_markup = menu_keyboard, parse_mode="Markdown")
	bot.telegram.send_message(message.u_id, btc_address, reply_markup = menu_keyboard, parse_mode="Markdown")
	bot.telegram.send_photo(message.u_id, qr_file)