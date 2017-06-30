from app import *
from bitcoin import *

wallets = pymongo_client["wallets"]

class Wallet():
	def __init__(self, uid):
		wallet = wallets.find({"uid":uid})
		if not wallet: wallet = _create_wallet()

		self.addres = wallet["addres"]
		self.public = wallet["public"]
		self.private = wallet["private"]

	def _create_wallet():
		key = random_key()
		private = sha256(key) 
		public = privtopub(private)
		addres = pubtoaddr(pub)

		wallet = {"private": private,
				  "public": public,
				  "addres": addres}

		return wallet

	def send_money(value, addres):
		pass


