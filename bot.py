import telebot
from os import getenv


API_TOKEN = getenv('API_TOKEN')

bot = telebot.TeleBot(API_TOKEN)
