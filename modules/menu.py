# -*- coding:utf-8 -*-?

import telebot
from wallet import Wallet


def init(bot):
    bot.handlers["main-menu"] = menu

def menu(bot, message):
	keyboard = bot.get_keyboard("menu-keyboard")
	menu_message = bot.render_message("menu-message")
	wallet_message = bot.render_message("wallet-created")

	if not bot.user_get(message.u_id, "wallet"):
		wallet = Wallet(bot, message.u_id)

		bot.telegram.send_message(message.u_id, wallet_message, reply_markup=keyboard, parse_mode="Markdown")

	key = bot.get_key("menu-keyboard", message.text)
	if key:
		bot.call_handler(key, message, forward_flag=False)
	else:
		bot.telegram.send_message(message.u_id, menu_message, reply_markup=keyboard)