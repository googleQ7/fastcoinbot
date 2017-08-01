from app import *
from bitcoin import *


wallets = pymongo_client["wallets"]
COMISSION = app.comission 

class Wallet():
	def __init__(self, uid):
		wallet = wallets.find({"uid":uid})
		if not wallet: wallet = _create_wallet()

		self.address = wallet["address"]
		self.public = wallet["public"]
		self.private = wallet["private"]

	def _create_wallet(self):
		key = random_key()
		private = sha256(key) 
		public = privtopub(private)
		address = pubtoaddr(pub)

		wallet = {"private": private,
				  "public": public,
				  "address": address}

		return wallet

	def get_balance(self):
		return 0

	def send_money(self, value, address):
		h = history(self.addres)
		
		balance = self.get_balance()

		outs = [{'value': value, 'address': address}
				{'velue': balance - COMISSION, 'address': self.address}]

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

