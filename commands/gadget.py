import json
import random
import math
import time

from utils.log import logger
from utils.config import group
import utils.caiyun as cy
import utils.connect as ct


def roll(update, context):

    logger.info(f'\\roll {update.message.chat_id} {json.dumps(context.args)}')

    try:
        random.seed(math.floor(time.time()))
        context.bot.send_message(
            update.message.chat_id, 'Choose: '+str(random.randint(1, int(context.args[0]))))
    except:
        context.bot.send_message(
            update.message.chat_id, 'Usage: /roll [total]')


def echo(update, context):
    logger.info('\\echo {}'.format(' '.join(context.args)))
    context.bot.send_message(group, ' '.join(context.args))


def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def new_message(update, context):
    cy.newmsg = 0


emoji = '👮🚔🚨🚓'


def callpolice(update, context):

    logger.info(f'\\callpolice {update.message.chat_id}')
    random.seed(math.floor(time.time()))

    text = ''
    for _ in range(random.randint(10, 100)):
        text += emoji[random.randint(0, 3)]
    context.bot.send_message(chat_id=update.message.chat_id, text=text)
