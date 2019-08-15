# -*- coding: utf-8 -*-
# @Author: Konano
# @Date:   2019-05-28 14:12:29
# @Last Modified by:   Konano
# @Last Modified time: 2019-08-15 23:52:47

import time
from socket import *
from threading import Thread, Lock

connectTimeLimit = 10

import configparser
import crawler

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
# logging.info(mute_list)

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

rain_UPDATE = 0

def rain_thu(bot, job):

    global rain_UPDATE

    if rain_UPDATE == 0:
        return

    try:
        if rain_UPDATE == +1:
            bot.send_message(chat_id=group, text='下雨了。')
        elif rain_UPDATE == -1:
            bot.send_message(chat_id=group, text='雨停了。')
    except:
        pass

    rain_UPDATE = 0


def forecast(bot, update):

    bot.send_message(chat_id=group, text=caiyunData['result']['forecast_keypoint'])

def forecast_hourly(bot, update):

    bot.send_message(chat_id=group, text=caiyunData['result']['hourly']['description'])

base_probability = 0.7
rain_4h = False
pre_start = pre_end = 0

def forecast_rain(bot):

    probability_2h = caiyunData['result']['minutely']['probability']
    probability_4h = caiyunData['result']['minutely']['probability_4h']
    global rain_4h
    if max(probability_4h) < base_probability:
        rain_4h = False
    elif max(probability_2h) < base_probability:
        if rain_4h == False:
            rain_4h = True
            bot.send_message(chat_id=group, text='There will be precipitation in 4 hours.')
    else:
        precipitation = np.array(caiyunData['result']['minutely']['precipitation_2h'])
        global pre_start, pre_end
        rain_start = np.argmax(precipitation >= 0.03)
        rain_end = np.argmax(precipitation < 0.03)
        if (pre_start == 0  and rain_start > 0) or \
           (pre_start >= 60 and rain_start < 60) or \
           (pre_start >= 30 and rain_start < 30) or \
           (pre_end == 0  and rain_end > 0) or \
           (pre_end >= 60 and rain_end < 60) or \
           (pre_end >= 30 and rain_end < 30):
            bot.send_message(chat_id=group, text=caiyunData['result']['forecast_keypoint'])
        pre_start = rain_start
        pre_end = rain_end

caiyunFailedCount = 0

def caiyun(bot, job):

    global caiyunData
    caiyunData = json.loads(crawler.request('https://api.caiyunapp.com/v2/{}/{},{}/weather.json?lang=en_US' \
        .format(config['CAIYUN']['token'], config['CAIYUN']['longitude'], config['CAIYUN']['latitude'])))

    with open('data/caiyun.json', 'w') as file:
        json.dump(caiyunData, file)

    if caiyunData['status'] != 'ok':
        logging.warning('Failed to get CaiYun data.')
        caiyunFailedCount += 1
        if caiyunFailedCount == 5:
            bot.send_message(chat_id=group, text='Failed to get CaiYun data 5 times.')
        return
    else:
        caiyunFailedCount = 0

    forecast_rain(bot)


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

w_REQUEST = False
w_DATA = {}

def weather_thu(bot, update):

    logging.info('\\weather_thu')

    try:
        global serverSocket
        serverSocket.send('W'.encode('utf8'))
        logging.info('Send request')
    except:
        logging.exception('Connect Error')
        return

    try:
        global w_REQUEST
        w_REQUEST = True
        cnt = 10 * connectTimeLimit
        while w_REQUEST:
            time.sleep(0.1)
            cnt -= 1
            if cnt <= 0:
                raise
    except:
        bot.send_message(update.message.chat_id, 'Time out: %ds'%connectTimeLimit)
        logging.warning('Don\'t receive any data in %ds'%connectTimeLimit)
        return

    logging.info('Received data')
    text = ''
    for station in w_DATA:
        if text != '':
            text += '\n'
        text += station['location'] + '\n'
        text += station['date'] + ' ' + station['time'] + '\n'
        text += '{}°C  {}%  {}m/s  {}mm\n'.format(station['temperature'], station['humidity'], station['wind_speed'], station['rainfall_10mins'])
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
                serverSocket.settimeout(300)
                msg = serverSocket.recv(65536).decode('utf8')
            except timeout:
                serverSocket.send('T'.encode('utf8'))
                try:
                    serverSocket.settimeout(3)
                    serverSocket.recv(8)
                except timeout:
                    raise
                else:
                    TESTSUC += 1
                    if TESTSUC % 10 == 0:
                        logging.info('TESTSUC * 10')
                    continue

            logging.info(msg)
            if msg == '':
                raise
            if msg[0] == 'W':     # weather
                global w_REQUEST, w_DATA
                w_DATA = json.loads(msg[1:])
                w_REQUEST = False
                serverSocket.send('S'.encode('utf8'))
            elif msg[0] == 'R':
                logging.info(msg)
                global rain_UPDATE
                if msg[1] == 'S':
                    rain_UPDATE = +1
                elif msg[1] == 'E':
                    rain_UPDATE = -1
                serverSocket.send('S'.encode('utf8'))
            else:
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


def killed(bot, update):

    if update.message.chat_id != owner:
        return
    logging.info('\\kill')

    try:
        global serverSocket
        serverSocket.send('K'.encode('utf8'))
        logging.info('Send request')
    except:
        logging.exception('Connect Error')
        return

    bot.send_message(owner, 'Killed.')


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
    dp.add_handler(CommandHandler('weather_thu', weather_thu))
    dp.add_handler(CommandHandler('kill', killed))
    dp.add_handler(CommandHandler('forecast', forecast))
    dp.add_handler(CommandHandler('forecast_hourly', forecast_hourly))

    updater.job_queue.run_repeating(info, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(rain_thu, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(caiyun, interval=300, first=0, context=group)

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    connect = Thread(target=connectSocket)
    connect.start()
    main()