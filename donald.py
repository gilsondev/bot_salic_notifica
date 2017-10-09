import sys
import sqlite3
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import urllib.request, json
from urllib.request import urlopen
# from telegram.ext import Updater
from telegram.ext import Updater, CommandHandler, Job
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi! Use /set <minutes> to set a timer')


def alarm(bot, job):
    conn=sqlite3.connect('salic.db')
    """Function to send the alarm message"""
    with urllib.request.urlopen("http://api.salic.cultura.gov.br/v1/projetos/?limit=1&sort=PRONAC:desc&format=json") as url:
        data = json.loads(url.read().decode('utf-8'))
    

    noticia = data 
    menssagem =  'Nova Proposta de #Projeto aceita pelo MinC:' + '\n\n' + 'Nome do Projeto: ' + noticia['_embedded']['projetos'][0]['nome'] +'\n\n'+ 'Pronac do Projeto: ' + noticia['_embedded']['projetos'][0]['PRONAC'] +'\n\n'+ 'Area do Projeto: ' + noticia['_embedded']['projetos'][0]['area'] +'\n\n'+ 'Segmento: ' + noticia['_embedded']['projetos'][0]['segmento'] + '\n\n'+ 'Cidade: '+ noticia['_embedded']['projetos'][0]['municipio']+'-'+ noticia['_embedded']['projetos'][0]['UF'] +'\n\n'+ 'Valor da Proposta: R$ '+ str(noticia['_embedded']['projetos'][0]['valor_proposta'])+'\n\n'+ 'Resumo do Projeto: ' + noticia['_embedded']['projetos'][0]['resumo'] +'\n\n'+ 'Acompanhe a execução deste projeto no Versalic em:\n' + 'http://versalic.cultura.gov.br/#/projetos/'+ noticia['_embedded']['projetos'][0]['PRONAC'] +'\n\n'+ 'Mais sobre a Lei Rouanet em Rouanet.cultura.gov.br'
    sql = 'SELECT PRONAC FROM salicBot WHERE cod = 2'
    curs = conn.cursor()
    teste = curs.execute(sql)
    teste2 = curs.fetchone()

    if str('('+noticia['_embedded']['projetos'][0]['PRONAC']+',)') != str(teste2):
        
        params =  (noticia['_embedded']['projetos'][0]['PRONAC'],noticia['_embedded']['projetos'][0]['PRONAC'])
        sql1 = 'UPDATE salicBot SET PRONAC = ? WHERE PRONAC < ?'
        curs = conn.cursor()
        curs.execute(sql1,params)
        conn.commit()
        conn.close() 


    
        # -------------------------
        bot.sendMessage(job.context, text=menssagem)
        # -------------------------
    elif str('('+noticia['_embedded']['projetos'][0]['PRONAC']+',)') == str(teste2):
        pass
    else:
        bot.sendMessage(job.context, text='error')
    # bot.sendMessage(job.context, text=menssagem)
    # bot.send_message(job.context, text='Beep!')


def set(bot, update, args, job_queue, chat_data):
    """Adds a job to the queue"""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0]) #* 60 #essa multiplicação é para tornar em minutos!!!!!
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_repeating(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <minutes>')


def unset(bot, update, chat_data):
    """Removes the job if the user changed their mind"""

    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def main():
    updater = Updater("394913941:AAF0moTdE_d2-sAyv7kLO9GGV66SrViGJOc")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("set", set,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
    