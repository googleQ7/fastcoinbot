from wallet import Wallet

def init(bot):
	bot.handlers["get-money"] = get_money

def get_money(bot, message):
	wallet = Wallet(bot, message.u_id)

	keyboard = bot.get_keyboard("menu-keyboard")
	info = bot.render_message("get-money", address=wallet.address)
	bot.telegram.send_message(message.u_id, info, reply_markup = keyboard, parse_mode="Markdown")