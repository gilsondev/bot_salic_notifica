import sys
import sqlite3
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.request, json
from urllib.request import urlopen
from telegram.ext import Updater, CommandHandler, Job
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)


def alarm(bot, job):
    conn=sqlite3.connect('teste.db')
    
    with urllib.request.urlopen("http://api.salic.cultura.gov.br/v1/projetos/?limit=3&sort=PRONAC:desc&format=json") as url:
        data = json.loads(url.read().decode('utf-8'))
    
    array = ([])
    noticia = data 
    
    for i in range(3):
        array.append(noticia['_embedded']['projetos'][i]['PRONAC'])
    

    y = (0,1,2)
    for x in reversed(y):
        print (x)
        menssagem =  'Nova Proposta de #Projeto aceita pelo MinC:' + '\n\n' + 'Nome do Projeto: ' + noticia['_embedded']['projetos'][x]['nome'] +'\n\n'+ 'Pronac do Projeto: ' + noticia['_embedded']['projetos'][x]['PRONAC'] +'\n\n'+ 'Area do Projeto: ' + noticia['_embedded']['projetos'][x]['area'] +'\n\n'+ 'Segmento: ' + noticia['_embedded']['projetos'][x]['segmento'] + '\n\n'+ 'Cidade: '+ noticia['_embedded']['projetos'][x]['municipio']+'-'+ noticia['_embedded']['projetos'][x]['UF'] +'\n\n'+ 'Valor da Proposta: R$ '+ str(noticia['_embedded']['projetos'][x]['valor_proposta'])+'\n\n'+ 'Resumo do Projeto: ' + noticia['_embedded']['projetos'][x]['resumo'] +'\n\n'+ 'Acompanhe a execução deste projeto no Versalic em:\n' + 'http://versalic.cultura.gov.br/#/projetos/'+ noticia['_embedded']['projetos'][x]['PRONAC'] +'\n\n'+ 'Mais sobre a Lei Rouanet em Rouanet.cultura.gov.br'
        params =  (noticia['_embedded']['projetos'][x]['PRONAC'],)
        
        sql = 'SELECT PRONAC = ? FROM salicBot WHERE cod = 1'
        curs = conn.cursor()
        teste = curs.execute(sql,params)
        teste2 = curs.fetchall()
        teste3 = curs.fetchone()
        
        if str('[(0,), (0,), (0,)]') == str(teste2):
            print ('certo')
            bot.sendMessage(job.context, text=menssagem)
    for p in range(3):

        params1 =  (noticia['_embedded']['projetos'][p]['PRONAC'],(p+1))
        sql1 = 'UPDATE salicBot SET PRONAC = ? WHERE id = ?'
        curs = conn.cursor()
        curs.execute(sql1,params1)
        conn.commit()
      

    conn.close()



def set(bot, update, job_queue, chat_data):

    chat_id = update.message.chat_id
    # chat_id = '@projetosMinc'
    try:
        
        due = 1 #* 60 #essa multiplicação é para tornar em minutos!!!!!
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        
        job = job_queue.run_repeating(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Agora você receberá os Projetos aprovados do Salic no Canal @projetosMinc')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /start')


def main():
    updater = Updater(sys.argv[0])


    dp = updater.dispatcher



    dp.add_handler(CommandHandler("start", set,
                                  pass_job_queue=True,
                                  pass_chat_data=True))


    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
