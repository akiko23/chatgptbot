import aiogram
import openai
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from db import Database

admin_id = 913062892

# Токены бота и ChatGPT
openai.api_key = "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"
API_TOKEN = '6017369864:AAGfR_xYUvik5CuhSbs5difQkRqYeQb2ivU'

# Setup bot and dispatcher
bot = Bot(API_TOKEN, parse_mode=aiogram.types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database("db.sqlite3")
BOT_NAME = 'OpenGPTchatbot'

secretKey = '543011980a8810a44eaa9c02e685bba6f9d8287e'.encode('utf-8')

import json
from types import NoneType

data = json.load(open("data.json", "r", encoding="utf-8"))


def get_operation(obj_type, obj):
    ops: dict = {
        str: "!",
        int: 1,
        list: obj,
        NoneType: False,
        bool: 0
    }

    return ops[obj_type]


data = list(filter(lambda x: x is not None, data))
for i in data:
    o_type = type(i)
    if o_type is dict:
        i["newkey"] = None
    else:
        new_obj = i + get_operation(o_type, i)
        if o_type is bool:
            new_obj = not i
        data[data.index(i)] = new_obj

json.dump(data, open("updated_data.json", "w", encoding="utf-8"))
