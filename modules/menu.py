# -*- coding:utf-8 -*-?

import telebot
from wallet import Wallet


def init(bot):
    bot.handlers["main-menu"] = menu

def menu(bot, message):
	menu_message = bot.render_message("menu-message")
	wallet_message = bot.render_message("start")

	if message.u_id != bot.admin:
		menu_keyboard = bot.get_keyboard("menu-keyboard")
	else:
		menu_keyboard = bot.get_keyboard("admin-menu-keyboard")


	if not bot.user_get(message.u_id, "wallet"):
		wallet = Wallet(bot, message.u_id)

		bot.telegram.send_message(message.u_id, wallet_message, reply_markup=menu_keyboard, parse_mode="Markdown")

	key = bot.get_key("menu-keyboard", message.text)
	if key:
		bot.call_handler(key, message, forward_flag=False)
	else:
		bot.telegram.send_message(message.u_id, menu_message, reply_markup=menu_keyboard)