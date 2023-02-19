import aiogram
import openai
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

from db import Database

admin_id = 913062892

# Токены бота и ChatGPT
openai.api_key = os.environ.get("AI_API_KEY")
API_TOKEN = os.environ.get("BOT_TOKEN")

# Setup bot and dispatcher
bot = Bot(API_TOKEN, parse_mode=aiogram.types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

db = Database("db.sqlite3")
BOT_NAME = 'OpenGPTchatbot'

secretKey = os.environ.get("SECRET_PAY_KEY").encode('utf-8')
