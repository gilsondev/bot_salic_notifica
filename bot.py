import sys
import sqlite3
import time
import telepot
# import feedparser
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.request, json
from urllib.request import urlopen
from telegram.ext import Updater

# Para testar o loop de enviar msg a cada 5min
# u = Updater('394913941:AAF0moTdE_d2-sAyv7kLO9GGV66SrViGJOc')
# j = u.job_queue

def on_chat_message(msg):
    conn=sqlite3.connect('salic.db')
    with urllib.request.urlopen("http://api.salic.cultura.gov.br/v1/projetos/?limit=1&sort=PRONAC:desc&format=json") as url:
        data = json.loads(url.read().decode('utf-8'))
    content_type, chat_type, chat_id = telepot.glance(msg)

    noticia = data
    menssagem =  'Nova Proposta de #Projeto aceita pelo MinC:' + '\n\n' + 'Nome do Projeto: ' + noticia['_embedded']['projetos'][0]['nome'] +'\n\n'+ 'Pronac do Projeto: ' + noticia['_embedded']['projetos'][0]['PRONAC'] +'\n\n'+ 'Area do Projeto: ' + noticia['_embedded']['projetos'][0]['area'] +'\n\n'+ 'Segmento: ' + noticia['_embedded']['projetos'][0]['segmento'] + '\n\n'+ 'Cidade: '+ noticia['_embedded']['projetos'][0]['municipio']+'-'+ noticia['_embedded']['projetos'][0]['UF'] +'\n\n'+ 'Valor da Proposta: R$ '+ str(noticia['_embedded']['projetos'][0]['valor_proposta'])+'\n\n'+ 'Resumo do Projeto: ' + noticia['_embedded']['projetos'][0]['resumo'] +'\n\n'+ 'Acompanhe a execução deste projeto no Versalic em:\n' + 'http://versalic.cultura.gov.br/#/projetos/'+ noticia['_embedded']['projetos'][0]['PRONAC'] +'\n\n'+ 'Mais sobre a Lei Rouanet em Rouanet.cultura.gov.br'
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Hit me up', callback_data='press')],
               ])
    # def callback_minute(bot, job):
    #     bot.sendMessage(chat_id, text=menssagem)
    # job_minute = j.run_repeating(callback_minute, interval=10, first=0)

    #CERTO ABAIXOOOO -------------------

    bot.sendMessage(chat_id, text=menssagem)
    # -------------------------


    # params =  (noticia['_embedded']['projetos'][0]['PRONAC'], noticia['_embedded']['projetos'][0]['nome'])
    # sql = ''' INSERT INTO salicBot(PRONAC, nome)
    #               VALUES(?,?)'''
    # curs = conn.cursor()
    # curs.execute(sql,params)
    # conn.commit()
    # conn.close()


    # TENTANDO RESOLVER PROBLEMA DE ATUALIZAR O BANCO
    # -----------------
    params =  (noticia['_embedded']['projetos'][0]['PRONAC'],noticia['_embedded']['projetos'][0]['PRONAC'])
    sql1 = 'UPDATE salicBot SET PRONAC = ? WHERE PRONAC < ?'
    curs = conn.cursor()
    curs.execute(sql1,params)
    conn.commit()
    conn.close()   

    # if (sql1 < noticia['_embedded']['projetos'][0]['PRONAC']):
    
    # curs = conn.cursor() 
    # curs.execute('UPDATE salicBot SET PRONAC =? ',[noticia['_embedded']['projetos'][0]['PRONAC']],)
    # conn.commit()
    # conn.close()




    
TOKEN = sys.arg[0]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, {'chat': on_chat_message}).run_as_thread()
print('Listening ...')



while 1:
    time.sleep(10)
