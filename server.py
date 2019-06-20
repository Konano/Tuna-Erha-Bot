# -*- coding: utf-8 -*-
# @Author: Konano
# @Date:   2019-05-28 14:12:29
# @Last Modified by:   Konano
# @Last Modified time: 2019-06-20 15:01:34

import time
from socket import *
from threading import Thread, Lock


import configparser

config = configparser.ConfigParser()
config.read('config.ini')
owner = config['BOT'].getint('owner')
group = config['BOT'].getint('group')

def update_config():
    with open('config.ini', 'w') as configFile:
        config.write(configFile)


import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s',
                    level=logging.INFO)
                    # level=logging.INFO,
                    # filename=config['BOT']['log'])
logger = logging.getLogger(__name__)


from telegram.ext import Updater, CommandHandler, Filters

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


# import crawler
import json

with open('data/mute.json', 'r') as file:
    mute_list = json.load(file)
logging.info(mute_list)

lock = Lock()
newMessages = []
info_UPDATE = False

def info(bot, job):

    global newMessages, info_UPDATE

    if info_UPDATE == False:
        return
    info_UPDATE = False

    lock.acquire()

    try:
        newMessages = [each for each in newMessages if each['source'] not in mute_list]

        if newMessages != []:
            logging.info('Detected new messages: ' + str(len(newMessages)))
            for each in newMessages:
                bot.send_message(chat_id=group,
                                 text='Info %s\n[%s](%s)' % (each['source'], each['title'], each['url']),
                                 parse_mode='Markdown')
    except:
        pass

    lock.release()

def mute(bot, update, args):

    if update.message.chat_id != owner and update.message.chat_id != group:
        return
    logging.info('\\mute '+json.dumps(args))

    text = ''
    for each in args:
        text += each
    if text == '':
        bot.send_message(update.message.chat_id, 'Usage: /mute [source]')
        return

    global mute_list
    mute_list.append(text)

    with open('data/mute.json', 'w') as file:
        json.dump(mute_list, file)

    bot.send_message(update.message.chat_id, 'Muted: ' + text)

def unmute(bot, update, args):

    if update.message.chat_id != owner and update.message.chat_id != group:
        return
    logging.info('\\unmute '+json.dumps(args))

    text = ''
    for each in args:
        text += each
    if text == '':
        bot.send_message(update.message.chat_id, 'Usage: /unmute [source]')
        return

    global mute_list
    mute_list.remove(text)

    with open('data/mute.json', 'w') as file:
        json.dump(mute_list, file)

    bot.send_message(update.message.chat_id, 'Unmuted: ' + text)

def setid(bot, update):

    if update.message.chat_id > 0 or update.effective_user.id != owner:
        return
    logging.info('\\setid')

    group = update.message.chat_id
    config['BOT']['group'] = str(group)
    update_config()

def mute_show(bot, update):

    if update.message.chat_id != owner and update.message.chat_id != group:
        return
    logging.info('\\mute_list')

    text = 'Muted list:'
    for each in mute_list:
        text += '\n' + each

    bot.send_message(update.message.chat_id, text)

TESTSUC = 0
def connectSocket():

    mainSocket = socket(AF_INET,SOCK_STREAM)
    mainSocket.bind((config['SERVER']['ip'], config['SERVER'].getint('port')))
    mainSocket.listen(1)

    global serverSocket
    logging.info('Wait for connection...')
    serverSocket,destAdr = mainSocket.accept()
    serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
    logging.info('Connect establish!')

    global TESTSUC
    while True:
        try:
            try:
                serverSocket.settimeout(60)
                msg = serverSocket.recv(65536).decode('utf8')
            except timeout:
                serverSocket.send('T'.encode('utf8'))
                try:
                    serverSocket.settimeout(5)
                    serverSocket.recv(8)
                except timeout:
                    raise
                else:
                    TESTSUC += 1
                    if TESTSUC % 60 == 0:
                        logging.info('TESTSUC * 60')
                    continue

            logging.info(msg)
            if msg == '':
                raise
            lock.acquire()
            try:
                global newMessages, info_UPDATE
                newMessages   = json.loads(msg)
                info_UPDATE   = True
            except:
                pass
            lock.release()
            serverSocket.send('S'.encode('utf8'))

        except:
            logging.exception('Connect Error')
            serverSocket.close()
            logging.info('Wait for connection...')
            serverSocket,destAdr = mainSocket.accept()
            serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
            serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
            serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
            serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
            logging.info('Connect establish!')
            continue

    serverSocket.close()
    mainSocket.close()


def main():

    if config['BOT'].getboolean('proxy'):
        updater = Updater(config['BOT']['accesstoken'], request_kwargs={'proxy_url': config['BOT']['socks5']})
    else:
        updater = Updater(config['BOT']['accesstoken'])

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('mute', mute, pass_args=True))
    dp.add_handler(CommandHandler('unmute', unmute, pass_args=True))
    dp.add_handler(CommandHandler('mute_list', mute_show))
    dp.add_handler(CommandHandler('setid', setid))

    updater.job_queue.run_repeating(info, interval=10, first=0, context=group)

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    connect = Thread(target=connectSocket)
    connect.start()
    # main()