from bitcoin import *
import requests

class Wallet():
	def __init__(self, bot, uid):
		wallet = bot.user_get(uid, "wallet")
		if not wallet: 
			wallet = self._create_wallet(uid)
			bot.user_set(uid, "wallet", wallet)	 
			
		self.address = wallet["address"]
		self.public = wallet["public"]
		self.private = wallet["private"]
		self.comission = bot.const["comission"]

	def _create_wallet(self, uid):
		key = random_key()
		private = sha256(key) 
		public = privtopub(private)
		address = pubtoaddr(public)

		wallet = {"private": private,
				  "public": public,
				  "address": address}

		return wallet

	def get_balance(self):
		res = requests.get("https://blockchain.info/balance?active=%s" % self.address).json()

		balance = res[self.address]["final_balance"]
		return balance

	def send_money(self, value, address):
		h = history(self.addres)
		
		balance = self.get_balance()

		outs = [{'value': value, 'address': address},
				{'velue': balance - self.comission, 'address': self.address}]

		try:
			tx = mktx(h, outs)
			for i in range(len(h)):
				tx = sign(tx, i, self.private)
		except Exception:
			return 1
		
		try:
			bci_pushtx(tx)
		except Exception:
			return 2

		return 0

