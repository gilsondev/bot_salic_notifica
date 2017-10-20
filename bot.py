# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import time
import telepot
import json
import urllib.request
import logging

from urllib.request import urlopen

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, Job
from telegram import ParseMode


SALIC_API_URI = "http://api.salic.cultura.gov.br/v1/"
PROJECTS_RESOURCE = "{0}projetos?limit=15&sort=PRONAC:desc&format=json".format(
    SALIC_API_URI
)
POSICOES = range(15)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

checkExist = '[(0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), (0,), '
'(0,), (0,), (0,), (0,), (0,), (0,)]'


def _fetch_projects():
    noticia = {}
    logger.info("Acessando recurso de projetos")
    with urllib.request.urlopen(PROJECTS_RESOURCE) as url:
        noticia = json.loads(url.read().decode('utf-8'))
        logger.debug("Projetos solicitados")

    return noticia


def alarm(bot, job):
    conn = sqlite3.connect('bot.db')

    projetos = _fetch_projects()

    for posicao in reversed(POSICOES):
        projeto = projetos['_embedded']['projetos'][posicao]

        mensagem = """
        Nova Proposta de #Projeto aceita pelo MinC:

        *Nome do Projeto*: {projeto}

        *Pronac do Projeto*: {pronac}

        *Area do Projeto*: {area}

        *Segmento*: {segmento}

        *Cidade*: {cidade} - {estado}

        *Valor da Proposta*: `R$ {valor_proposta}`

        *Resumo do Projeto*: {resumo_projeto}

        Acompanhe a execução deste projeto no *Versalic* em:
        http://versalic.cultura.gov.br/#/projetos/{pronac}

        Mais sobre a *Lei Rouanet* em:
        http://rouanet.cultura.gov.br
        
        """.format(
            projeto=projeto['nome'],
            pronac=projeto['PRONAC'],
            area=projeto['area'],
            segmento=projeto['segmento'],
            cidade=projeto['municipio'],
            estado=projeto['UF'],
            valor_proposta=projeto['valor_proposta'],
            resumo_projeto=projeto['resumo']
        )

        params = (projeto['PRONAC'],)

        sql = 'SELECT PRONAC = ? FROM salicBot WHERE cod = 1'
        cursor = conn.cursor()
        teste = cursor.execute(sql, params)
        teste2 = cursor.fetchall()
        teste3 = cursor.fetchone()

        if checkExist == str(teste2):
            logger.debug("Exibindo mensagem...")
            bot.sendMessage(job.context, text=mensagem,
                            parse_mode=ParseMode.MARKDOWN)

    for posicao_atual in POSICOES:
        params = (projeto['PRONAC'], (posicao_atual + 1))
        update_salicbot_sql = 'UPDATE salicBot SET PRONAC = ? WHERE id = ?'
        cursor = conn.cursor()
        cursor.execute(update_salicbot_sql, params)
        conn.commit()

    conn.close()


def start(bot, update, job_queue, chat_data):

    chat_id = update.message.chat_id

    try:

        due = 1  # * 60 #essa multiplicação é para tornar em minutos!!!!!
        if due < 0:
            update.message.reply_text('Não podemos ir para o futuro!')
            return

        logger.debug("Iniciando job...")
        job = job_queue.run_repeating(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text(
            'Agora você receberá os Projetos aprovados '
            'do Salic no Canal @projetosMinc'
        )

    except (IndexError, ValueError):
        update.message.reply_text('Use: /start')


def main():

    updater = Updater(os.environ.get('SALIC_BOT_TOKEN'))

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start,
                                          pass_job_queue=True,
                                          pass_chat_data=True))

    updater.start_polling(timeout=240, clean=False)
    updater.idle()


if __name__ == '__main__':
    main()
