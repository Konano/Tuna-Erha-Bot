import json
import random
import math
import time
import re
import os
import qrcode
from PIL import Image
import numpy as np
import traceback

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


dig = np.array([
    [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
    [0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1],
    [1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1],
]) * 255


def generator_register(id, tm):

    try:
        pic = f'pic/{id}_{tm}.png'
        if not os.path.exists(pic):
            tmp = f'pic/{int(time.time())}.png'
            qrcode.make(id).save(tmp)
            bg = np.array(Image.open('template/template.jpg').convert('L'))
            tmp = np.array(Image.open(tmp).convert('L'))[40:-45, 40:-45]
            tmp = np.array(Image.fromarray(tmp).resize((41, 41)))
            bg[14:55, 25:66] = tmp
            points = [29, 35, 41, 47, 53, 59]
            edit = [int(_) for _ in tm]
            for i in range(6):
                x, y, d = 55, points[i], edit[i]
                bg[x:x+7, y:y+4] = dig[d].reshape(7, 4)
            Image.fromarray(bg).save(pic)
        return pic
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.error(e)


def register(update, context):

    logger.info(
        f'\\register {update.message.chat_id} {json.dumps(context.args)}')

    try:
        assert len(context.args) == 2
        assert len(re.findall(r'^\d{10}$', context.args[0])) == 1
        assert len(re.findall(r'^\d{6}$', context.args[1])) == 1

        pic = generator_register(context.args[0], context.args[1])
        context.bot.send_photo(
            chat_id=update.message.chat_id, photo=open(pic, 'rb'))

    except:
        context.bot.send_message(
            update.message.chat_id, 'Usage: /register [StudentID] [Month]\nExample: /register 1994990239 202102')


hitcount = 0
hitchatid = {}

def hitreds(update, context):
    global hitcount
    hitcount += 1
    if update.message.chat_id not in hitchatid.keys():
        hitchatid[update.message.chat_id] = 0
    hitchatid[update.message.chat_id] += 1
    context.bot.send_message(update.message.chat_id, f'今日打红人 ({hitcount}/1)', reply_to_message_id=update.message.message_id)


def hitreds_init(context):
    global hitcount, hitchatid
    for chatid in hitchatid.keys():
        group_or_chat = '本群' if chatid < 0 else '您'
        context.bot.send_message(chatid, f'红人昨日被打次数: {hitcount}\n{group_or_chat}昨日打红人次数: {hitchatid[chatid]}\n红人 @ZenithalH 万分感谢您的支持！')
    hitcount = 0
    hitchatid = {}
