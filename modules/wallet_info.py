from wallet import Wallet


def init(bot):
	bot.handlers["wallet-info"] = wallet_info


def wallet_info(bot, message):
	wallet = Wallet(bot, message.u_id)

	keyboard = bot.get_keyboard("menu-keyboard")
	info = bot.render_message("wallet-info", balance=wallet.get_balance())
	bot.telegram.send_message(message.u_id, info, reply_markup = keyboard, parse_mode="Markdown")

