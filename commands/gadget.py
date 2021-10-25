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
from pathlib import Path
import io
from pyzbar.pyzbar import decode
from telegram import InputMediaPhoto

import utils.caiyun as cy
from utils.log import logger
from utils.config import group, hitred_aim
from utils.pool import add_pool
from utils.format import escaped


def roll(update, context):

    logger.info(f'\\roll {update.message.chat_id} {json.dumps(context.args)}')

    try:
        random.seed(math.floor(time.time()))
        update.message.reply_text('Choose: '+str(random.randint(1, int(context.args[0]))))
    except:
        update.message.reply_text('Usage: /roll [total]')


def echo(update, context):
    logger.info('\\echo {}'.format(' '.join(context.args)))
    context.bot.send_message(group, ' '.join(context.args))


def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def new_message(update, context):
    cy.update_newmsg()


emoji = '👮🚔🚨🚓'


def callpolice(update, context):

    logger.info(f'\\callpolice {update.message.chat_id}')
    random.seed(math.floor(time.time()))

    text = ''
    for _ in range(random.randint(10, 100)):
        text += emoji[random.randint(0, 3)]
    update.effective_chat.send_message(text)


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

    args = context.args

    logger.info(
        f'\\register {update.message.chat_id} {json.dumps(args)}')

    try:
        assert len(args) == 2
        assert len(re.findall(r'^\d{10}$', args[0])) == 1
        assert len(re.findall(r'^\d{6}$', args[1])) == 1

        pic = generator_register(args[0], args[1])
        update.message.reply_photo(open(pic, 'rb'))
        Path(pic).unlink()

    except:
        update.message.reply_text('Usage: /register [StudentID] [Month]\nExample: /register 1994990239 202102')


try:
    hitcount, hitchatid = json.load(open('data/hitred.json', 'r'))
    hitchatid = dict((int(k), hitchatid[k]) for k in hitchatid.keys())
except Exception as e:
    logger.debug(traceback.format_exc())
    logger.error(e)
    hitcount, hitchatid = 0, {}


def hitreds(update, context):
    global hitcount, hitchatid
    hitcount += 1
    if update.message.chat_id not in hitchatid.keys():
        hitchatid[update.message.chat_id] = 0
    try:
        msg = update.message.reply_text(f'打红人计数器 ({hitcount}/{hitred_aim})')
        add_pool(msg)
        hitchatid[update.message.chat_id] += 1
        json.dump([hitcount, hitchatid], open('data/hitred.json', 'w'))
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.error(e)


def hitreds_init(context):
    global hitcount, hitchatid
    __hitchatid = hitchatid
    hitchatid = {}
    json.dump([hitcount, hitchatid], open('data/hitred.json', 'w'))

    today_hitcount = 0
    for x in __hitchatid.keys():
        today_hitcount += __hitchatid[x]

    for chatid in __hitchatid.keys():
        group_or_chat = '本群' if chatid < 0 else '您'
        try:
            context.bot.send_message(
                chatid, f'红人昨日被打次数: {today_hitcount}\n{group_or_chat}昨日打红人次数: {__hitchatid[chatid]}\n红人 @ZenithalH 万分感谢您的支持！')
        except Exception as e:
            logger.debug(traceback.format_exc())
            logger.error(e)


users = {}


def yue(update, context) -> None:
    user_id = update.message.from_user.id
    user_name = update.message.from_user.name
    users[user_id] = user_name
    update.message.reply_text('约😘')


def gu(update, context) -> None:
    user_id = update.message.from_user.id
    if user_id in users:
        del users[user_id]
    update.message.reply_text('不约😭')


def fan(update, context) -> None:
    if len(users) == 0:
        update.message.reply_text('没人约😭')
        return
    info = ' '.join([f'[{escaped(user_name)}](tg://user?id={user_id})'
                     for user_id, user_name in users.items()])
    update.message.reply_markdown_v2(info)


def san(update, context) -> None:
    global users
    users = {}
    update.message.reply_text('散🎉')


def payme_upload(update, context) -> None:

    user_id = update.message.from_user.id
    folder = Path(f'pic/pay/{user_id}')
    folder.mkdir(exist_ok=True)
    try:
        buf = update.message.photo[-1].get_file().download_as_bytearray()
        for res in decode(Image.open(io.BytesIO(buf))):
            url = res.data.decode()
            if url.startswith('https://qr.alipay.com/'):
                with (folder / 'ali.png').open('wb') as f:
                    f.write(buf)
                update.message.reply_text('检测到：Alipay 收款码')
                return
            elif url.startswith('wxp://'):
                with (folder / 'wx.png').open('wb') as f:
                    f.write(buf)
                update.message.reply_text('检测到：Wechat 收款码')
                return
            elif url.startswith('https://qr.95516.com/'):
                with (folder / 'uni.png').open('wb') as f:
                    f.write(buf)
                update.message.reply_text('检测到：UnionPay 收款码')
                return
            else:
                update.message.reply_text('Unsupported QRCode')
                logger.warning(url)
                return
    except Exception as e:
        update.message.reply_text('QRCode not found')
        logger.warning(e)


def payme(update, context) -> None:

    user_id = update.message.from_user.id
    folder = Path(f'pic/pay/{user_id}')
    if not (folder.exists() and len(list(folder.iterdir()))):
        update.message.reply_text('No QRCodes found, send to me first!')
        return
    images = [InputMediaPhoto(file.open('rb')) for file in folder.iterdir()]
    update.message.reply_media_group(images)
    return
