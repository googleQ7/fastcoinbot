import requests
import time
import copy
import random

from wallet import Wallet

from bitcoin import *

class MainWallet(Wallet):
	def __init__(self, bot, priv):
		self.bot = bot
		self.ttl = 35*60

		pub = privtopub(priv)
		addr = pubtoaddr(pub)

		self.private = priv
		self.public = pub
		self.address = addr
		self.comission = bot.const["comission"]

	def _compare_all_tx(self):
		tx_list = self.bot.user_get(0, "tx-list")
		for tx_id in copy.copy(tx_list):
			if time.time() <= tx["time"]:
				bot.uset_delete(0, "tx/%s" % tx_id)
				tx_list.remove(tx_id)

		self.bot.user_set(0, "tx-list", tx_list)

	def _compare_tx(self, tx):
		self._compare_all_tx()
		cur_balance = self.balance()
		
		for tx_id in copy.copy(tx_list):
			tx = self.bot.user_get(0, "tx/%s" % tx_id)
			cur_balance -= tx["value"]

		if cur_balance -= tx["value"] >= 0 and tx["value"] != 0:
			return True
		else:
			return False

	def generate_id():
		return "".join([random.choice("1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM") for i in range(23)])

	def add_tx(self, username, address, value):
		tx = {"id": self.generate_id(),
			"username": username, 
			"time": time.time(),
			"address": address,
			"value": value}

		
		if self._compare_tx(tx):
			self.bot.user_set(0, "tx/%s" % tx["id"], tx)
		
			tx_list = self.bot.user_get(0, "tx-list")
			tx_list.append(tx["id"])
			self.bot.user_set(0, "tx-list", tx_list)
			return 0
		else:
			return -1

	def confirm_tx(self, tx_id):
		tx_list = self.bot.user_get(0, "tx-list")
		tx = self.bot.user_get(0, "tx/%s" % tx_id)
		
		tx_list.remove(tx_id)
		self.bot.user_set(0, "tx-list", tx_list)
		bot.user_delete(0, "tx/%s" % tx_id)

		self.send_money(tx["value"], tx["address"])

	def not_confirm_tx(self, tx_id):
		tx_list = self.bot.user_get(0, "tx-list")
		tx = self.bot.user_get(0, "tx/%s" % tx_id)
		
		tx_list.remove(tx_id)
		self.bot.user_set(0, "tx-list", tx_list)
		bot.user_delete(0, "tx/%s" % tx_id)