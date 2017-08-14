import re
import os

from main_wallet import MainWallet


main_wallet = MainWallet(os.environ.get(""))
def init(bot):
	pass

def start(bot, message):
	get_value_message = bot.render_message("get-value-to-buy")

	bot.telegram.send_message(get_value_message)
	bot.set_next_handler("buy-money/get-value")

def get_value(bot, message):
	incorrect_value_message = bot.render_message("incorrect-value-to-buy")
	get_username_message = bot.render_message("get-username-to-buy")

	serach_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1}).*(?P<corency>(BTC|RUB))", message.text)
	if serach_result:
		value, btc = serach_result.group("value"), serach_result.group("curency")
		if value == "RUB":
			rub = btc  
			btc = btc/main_wallet.get_curency()
		else:
			rub = btc*main_wallet.get_curency()
	
		bot.telegram.send_message(get_username_message)
		bot.set_next_handler("buy-money/get-username")		
	
	else:
		bot.telegram.send_message(incorrect_value_message)
		bot.call_handler("buy-money/get-value", message)
		return

def get_name(bot, message):
	accept_message = bot.render_message("accept-buy")

	username = message.text

	bot.telegram.send_message(get_username_message)
	bot.set_next_handler("buy-money/accept")	


def accept(bot, message):
	pass


def admin_yes(bot, message):
	pass

def admin_no(bot, message):
	pass