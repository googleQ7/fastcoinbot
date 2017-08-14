from wallet import Wallet

import qrcode
import io


def init(bot):
	bot.handlers["get-money/start"] = start

def start(bot, message):
	wallet = Wallet(bot, message.u_id)

	keyboard = bot.get_keyboard("menu-keyboard")
	info = bot.render_message("get-money", address=wallet.address)
	
	
	qr_image = qrcode.make(wallet.address)
	qr_bytes = io.BytesIO()
	qr_image.save(qr_bytes, format='PNG')
	
	qr_file = io.BytesIO(qr_bytes.getvalue())

	bot.telegram.send_message(message.u_id, info, reply_markup = keyboard, parse_mode="Markdown")
	bot.telegram.send_photo(message.u_id, qr_file)