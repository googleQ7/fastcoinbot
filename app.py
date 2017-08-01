import os

import flask
import telebot


app = flask.Flask(__name__)
bot = telebot.TeleBot(token=os.environ["BOT_TOKEN"])
mongo_client = MongoClient(os.environ.get("MONGO_URL", default = "localhost"), 27017)
app.comission = 32000

if __name__ == "__main__":
	app.run(port=os.environ["PORT"])