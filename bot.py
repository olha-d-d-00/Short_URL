import os
import pymongo
from telebot.async_telebot import AsyncTeleBot

from funcs import Shortener

bot = AsyncTeleBot(os.environ["TG_TOKEN"], parse_mode=None)
mongo_client = pymongo.AsyncMongoClient("mongodb://admin:password@localhost:27017/")
db = mongo_client['shortener_db']
urls_collection = db["urls"]



@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(message, "Hello")


@bot.message_handler(commands=['statistic'])
async def send_statistics(message):
    user_id = message.from_user.id
    user_urls= await urls_collection.find({"user_id": user_id}).to_list()
    user_text = f"Your URLs: \n" + "".join([f"{itm.get("long_url"):.25}... -> {itm.get("short_url")} : {itm.get("counter_clicks")}\n" for itm in user_urls])
    await bot.reply_to(message, user_text)


@bot.message_handler(func=lambda message: True if message.text.startswith("https://") else False)
async def process_text_message(message):
    if message.text.startswith("https://"):
        short_url = await Shortener.create_short_url(urls_collection, message.text, message.from_user.id)
        await bot.send_message(message.chat.id, f"Short url: http://127.0.0.1:8000/{short_url}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(bot.polling())