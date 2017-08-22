import logging
import json
import random
import codecs
import redis
import os
import importlib

import telebot
import jinja2


logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level = logging.INFO)

class Bot:
    def __init__(self, bot_name="super-bot", debug=False):
        self.logger = logging.getLogger(bot_name)
        self.logger.info("Starting bot")

        self.handlers = {}
        self.debug = debug
        self.callback_handlers = {}

        self.logger.info("Load config")
        self.admin = int(os.environ["ADMIN"])
        self.const = {}
        self.const.update(json.loads(codecs.open("config/init.json", "r", "utf-8").read()))
        self.const["messages"] = json.loads(codecs.open("config/messages.json", "r", "utf-8").read())
        self.const["keyboards"] = json.loads(codecs.open("config/keyboards.json", "r", "utf-8").read())

        self.logger.info("Connect to Telegram")
        self.telegram = telebot.TeleBot(os.environ["BOT_TOKEN"])
        self.telegram.set_update_listener(self.proсess_updates)

        self.redis = redis.from_url(os.environ.get("REDIS_URL","redis://localhost:6379"))
        self.data = {}

        self.logger.info("Collect modules")
        self._collect_modules()

        self.logger.info("Ready")

    def _collect_modules(self):
        for module_name in os.listdir("modules"):
            if module_name.endswith(".py"):
                module = importlib.import_module("modules.%s" % module_name[:-3])
                module.init(self)


    def user_set(self, user_id, field, value, **kwargs):
        key = "user:%s:%s"%(user_id, field)
        value = json.dumps(value)
        self.redis.set(key, value, kwargs)
        
        self.logger.info("user:%s set[%s]>>\"%s\""%(user_id, field, value))

    def user_get(self, user_id, field, default=None):
        key = "user:%s:%s"%(user_id, field)
        value = self.redis.get(key)
        if type(value) is bytes: value = value.decode('utf-8')
            
        self.logger.info("user:%s get[%s]>>\"%s\""%(user_id, field, value))
        
        if value is None: value = default
        else: value = json.loads(value)
        
        return value

    def user_delete(self, user_id, field):
        key = "user:%s:%s"%(user_id, field)
        self.redis.delete(key)
        self.logger.info("user:%s delete[%s]"%(user_id, field))



    def set_next_handler(self, user_id, handler):
        self.user_set(user_id, "next_handler", handler)

    def call_handler(self, handler, message, forward_flag=True):
        self.logger.info("user:%s call_handler[%s]" % (message.u_id, handler))
        
        try:
            if forward_flag: message.forward = True
            self.handlers[handler](self, message)
        except Exception as ex:
            self.logger.error(ex)
            if self.debug: raise ex
    
    def proсess_updates(self, updates):
        if type(updates) is telebot.types.Update:
            if updates.message is not None: self._process_message(updates.message)
            if updates.callback_query is not None: self._process_callback(updates.callback_query)
            return

        for update in updates:
            if type(update) is telebot.types.Message: self._process_message(update)
            if type(update) is telebot.types.CallbackQuery: self._process_message(update)

    def _process_message(self, message):
        message.u_id = message.chat.id
        message.forward = False

        if message.text == self.const["menu-button"]: 
            self.set_next_handler(message.u_id, self.const["default-handler"])
            message.forward = True
        
        current_handler = self.user_get(message.u_id, "next_handler", default = self.const["default-handler"])
        self.set_next_handler(message.u_id, self.const["default-handler"])

        try:
            self.call_handler(current_handler, message, forward_flag=False)
        except Exception as ex:
            self.logger.error(ex)
            if self.debug: raise ex
            self.set_next_handler(message.u_id, self.const["default-handler"])
            self.call_handler(self.const["default-handler"], message)

    def _process_callback(self, query):
        query.u_id = query.message.chat.id
        query.message.u_id = query.u_id
        if query.data:
            callback = query.data.split("/")[0]
            try:
                self.logger.info("user:%s callback[%s]"%(query.u_id, query.u_id))
                self.callback_handlers[callback](self, query)
            except Exception as ex:
                self.logger.error(ex)
                if self.debug: raise ex
        else: self.logger.error("user:%s callback[None]"%(query.u_id))

    def render_message(self, key, **kwargs):
        messages = self.const["messages"][key]
        
        if type(messages) is list: message = random.choice(messages)
        else: message = messages

        message = jinja2.Template(message)

        return message.render(**kwargs)

    def get_keyboard(self, keyboard):
        if keyboard is None: 
            markup = telebot.types.ReplyKeyboardRemove()
        else:
            if type(keyboard) is str: keyboard =  self.const["keyboards"][keyboard]
            markup = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
            for row in keyboard:
                keyboard_row = []
                for col in row: 
                    if "--position" in col[1]:
                        keyboard_row.append(telebot.types.KeyboardButton(col[0], request_location = True))
                    else:
                        keyboard_row.append(telebot.types.KeyboardButton(col[0]))
                markup.row(*keyboard_row)
        
        return markup

    def get_inline_keyboard(self, keyboard, params = {}):
        if type(keyboard) is str: keyboard =  self.const["keyboards"][keyboard]
        markup = telebot.types.InlineKeyboardMarkup(row_width=3)
        for row in keyboard:
            keyboard_row = []
            for col in row:
                if "--url" in col[1]:
                    item_url =  params.get(col[1].split("/")[1])
                    if not item_url is None: keyboard_row.append(telebot.types.InlineKeyboardButton(col[0], url = item_url))
                elif "--data" in col[1]:
                    data =  params.get(col[1].split("/")[1])
                    if not data is None: 
                        col[1] = "/".join([col[1].split("/")[0], data])   
                        keyboard_row.append(telebot.types.InlineKeyboardButton(col[0], callback_data = col[1]))
                else:
                    keyboard_row.append(telebot.types.InlineKeyboardButton(col[0], callback_data = col[1]))
            markup.row(*keyboard_row)

        return markup

    def get_key(self, keyboard, message):
        if type(keyboard) is str: keyboard = self.const["keyboards"][keyboard]
        for row in keyboard:
            for col in row:
                if message == col[0]: return col[1]