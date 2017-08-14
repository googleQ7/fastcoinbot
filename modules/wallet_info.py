from wallet import Wallet


def init(bot):
	bot.handlers["wallet-info/start"] = start


def start(bot, message):
	wallet = Wallet(bot, message.u_id)

	keyboard = bot.get_keyboard("menu-keyboard")
	balance = wallet.get_balance()/10**8
	curecy = wallet.get_currency() * balance
	
	info = bot.render_message("wallet-info", balance=wallet.get_balance()/10**8, rub=curecy)
	bot.telegram.send_message(message.u_id, info, reply_markup = keyboard, parse_mode="Markdown")

