import sys
import time
import telepot
import feedparser
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.request, json
from urllib.request import urlopen
from telegram.ext import Updater

u = Updater('394913941:AAF0moTdE_d2-sAyv7kLO9GGV66SrViGJOc')
j = u.job_queue

with urllib.request.urlopen("http://api.salic.cultura.gov.br/v1/projetos/?limit=1&sort=PRONAC:desc&format=json") as url:
    data = json.loads(url.read().decode('utf-8'))




def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    noticia = data
    menssagem ='Nome do Projeto: ' + noticia['_embedded']['projetos'][0]['nome'] +'\n'+ 'Pronac do Projeto: ' + noticia['_embedded']['projetos'][0]['PRONAC'] +'\n'+ 'Area do Projeto: ' + noticia['_embedded']['projetos'][0]['area'] +'\n'+ 'Resumo do Projeto: ' + noticia['_embedded']['projetos'][0]['resumo']
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Hit me up', callback_data='press')],
               ])
    # def callback_minute(bot, job):
    #     bot.sendMessage(chat_id, text=menssagem)
    # job_minute = j.run_repeating(callback_minute, interval=10, first=0)

    #CERTO ABAIXOOOO -------------------
    bot.sendMessage(chat_id, text=menssagem)
    # -------------------------


    
TOKEN = '394913941:AAF0moTdE_d2-sAyv7kLO9GGV66SrViGJOc'  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()
print('Listening ...')



while 1:
    time.sleep(10)