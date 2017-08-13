import re
import os

from main_wallet import MainWallet


main_wallet = MainWallet(os.environ.get(""))
def init(bot):
	pass

def start(bot, message):
	bot.telegram.send_message("Введ")

def get_value(bot, message):
	serach_result = re.search("(?P<value>[0-9]{1,}([,.][0-9]{1,}){0,1}).*(?P<corency>(BTC|RUB))", message.text)
	if serach_result:
		value, btc = serach_result.group("value"), serach_result.group("curency")
		if value == "RUB":
			rub = btc  
			btc = btc/main_wallet.get_curency()
		else:
			rub = btc*main_wallet.get_curency()
	else:
		bot.telegram.send_message("Чото не так")
def get_name(bot, message):
	username = message.text

def confirm(bot, message):
	pass


def admin_yes(bot, message):
	pass

def admin_no(bot, message):
	pass