# -*- coding: utf-8 -*-
# @Author: Konano
# @Date:   2019-05-28 14:12:29
# @Last Modified by:   Konano
# @Last Modified time: 2019-10-17 10:24:47

import time
from socket import *
from threading import Thread, Lock
import crawler
import random
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
import json

import re
import binascii
from Crypto.Cipher import AES

connectTimeLimit = 10

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


from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


with open('data/mute.json', 'r') as file:
    mute_list = json.load(file)


def webvpn(url):

    encryStr = b'wrdvpnisthebest!'

    def encrypt(url):
        url = str.encode(url)
        cryptor = AES.new(encryStr, AES.MODE_CFB, encryStr, segment_size = 16*8)
        
        return bytes.decode(binascii.b2a_hex(encryStr)) + \
            bytes.decode(binascii.b2a_hex(cryptor.encrypt(url)))

    if url[0:7] == 'http://':
        url = url[7:]
        protocol = 'http'
    elif url[0:8] == 'https://':
        url = url[8:]
        protocol = 'https'

    v6 = re.match('[0-9a-fA-F:]+', url)
    if v6 != None:
        v6 = v6.group(0)
        url = url[len(v6):]

    segments = url.split('?')[0].split(':')
    port = None
    if len(segments) > 1:
        port = segments[1].split('/')[0]
        url = url[0: len(segments[0])] + url[len(segments[0]) + len(port) + 1:]

    try:
        idx = url.index('/')
        host = url[0: idx]
        path = url[idx:]
        if v6 != None:
            host = v6
        url = encrypt(host) + path
    except:
        if v6 != None:
            url = v6
        url = encrypt(url)

    if port != None:
        url = 'https://webvpn.tsinghua.edu.cn/' + protocol + '-' + port + '/' + url
    else:
        url = 'https://webvpn.tsinghua.edu.cn/' + protocol + '/' + url

    return url


lock = Lock()
newMessages = []
delMessages = []
info_UPDATE = False
today_news = {}
sended_news = {}

def info(bot, job):

    global newMessages, delMessages, info_UPDATE, today_news, sended_news

    if info_UPDATE == False:
        return
    info_UPDATE = False

    lock.acquire()

    try:
        for each in newMessages:
            if each['source'] not in today_news:
                today_news[each['source']] = []
            today_news[each['source']].append(each)

        if delMessages != []:
            logging.info('Detected del messages: ' + str(len(delMessages)))
            for each in delMessages:
                if each['url'] in sended_news:
                    bot.delete_message( chat_id=group,
                                        message_id=sended_news[each['url']])
                    del sended_news[each['url']]
                if each['source'] in today_news and each in today_news[each['source']]:
                    today_news[each['source']].remove(each)
                    if today_news[each['source']] == []:
                        del today_news[each['source']]

        newMessages = [each for each in newMessages if each['source'] not in mute_list]

        if newMessages != []:
            logging.info('Detected new messages: ' + str(len(newMessages)))
            for each in newMessages:
                msg = bot.send_message( chat_id=group,
                                        text='Info %s\n[%s](%s) [(webvpn)](%s)' % (each['source'], each['title'], each['url'], webvpn(each['url'])),
                                        parse_mode='Markdown',
                                        disable_web_page_preview=True)
                sended_news[each['url']] = msg.message_id
    except Exception as e:
        logging.error(e)
        
    newMessages = []
    delMessages = []

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
    except Exception as e:
        logging.error(e)

    rain_UPDATE = 0


def deal_precipitation(str):

    intensity = float(str)

    if intensity == 0:
        return '无'
    elif intensity < 0.03:
        return '毛毛雨'
    elif intensity < 0.25:
        return '小雨'
    elif intensity < 0.35:
        return '中雨'
    elif intensity < 0.48:
        return '大雨'
    else:
        return '暴雨'

def deal_skycon(str):

    switch = {
        'CLEAR_DAY': '晴',
        'CLEAR_NIGHT': '晴',
        'PARTLY_CLOUDY_DAY': '多云',
        'PARTLY_CLOUDY_NIGHT': '多云',
        'CLOUDY': '阴',
        'WIND': '大风',
        'HAZE': '雾霾',
        'RAIN': '雨',
        'SNOW': '雪'
    }
    try:
        return switch[str]
    except KeyError as e:
        return 'ERROR'

def level_aqi(str):

    aqi = int(str)
    if aqi <= 50: return '优'
    elif aqi <= 100: return '良'
    elif aqi <= 150: return '轻度污染'
    elif aqi <= 200: return '中度污染'
    elif aqi <= 300: return '重度污染'
    else: return '严重污染'

def level_windspeed(str):

    speed = float(str)
    if speed <= 0.2: return 'Lv 0'
    elif speed <= 1.5: return 'Lv 1'
    elif speed <= 3.3: return 'Lv 2'
    elif speed <= 5.4: return 'Lv 3'
    elif speed <= 7.9: return 'Lv 4'
    elif speed <= 10.7: return 'Lv 5'
    elif speed <= 13.8: return 'Lv 6'
    elif speed <= 17.1: return 'Lv 7'
    elif speed <= 20.7: return 'Lv 8'
    elif speed <= 24.4: return 'Lv 9'
    elif speed <= 28.4: return 'Lv 10'
    elif speed <= 32.6: return 'Lv 11'
    elif speed <= 36.9: return 'Lv 12'
    elif speed <= 41.4: return 'Lv 13'
    elif speed <= 46.1: return 'Lv 14'
    elif speed <= 50.9: return 'Lv 15'
    elif speed <= 56.0: return 'Lv 16'
    elif speed <= 61.2: return 'Lv 17'
    else: return 'Lv >17'

def forecast(bot, update):

    logging.info('\\forecast {}'.format(update.message.chat_id))

    pic = precipitation_graph()
    bot.send_photo(chat_id=update.message.chat_id, photo=open(pic, 'rb'), caption=caiyunData['result']['forecast_keypoint'])

def forecast_hourly(bot, update):

    logging.info('\\forecast_hourly {}'.format(update.message.chat_id))

    bot.send_message(chat_id=update.message.chat_id, text=caiyunData['result']['hourly']['description'])

def weather(bot, update):

    logging.info('\\weather {}'.format(update.message.chat_id))

    text = '清华当前天气情况：\n'
    text += '温度: {}C°\n'.format(caiyunData['result']['realtime']['temperature'])
    text += '湿度: {}%\n'.format(int(float(caiyunData['result']['realtime']['humidity'])*100))
    text += '风速: {}m/s ({})\n'.format(caiyunData['result']['realtime']['wind']['speed'], level_windspeed(caiyunData['result']['realtime']['wind']['speed']))
    text += '降水: {}\n'.format(deal_precipitation(caiyunData['result']['realtime']['precipitation']['local']['intensity']))
    text += '天气: {}\n'.format(deal_skycon(caiyunData['result']['realtime']['skycon']))
    text += 'AQI: {} ({})\n'.format(level_aqi(caiyunData['result']['realtime']['aqi']), caiyunData['result']['realtime']['aqi'])

    bot.send_message(chat_id=update.message.chat_id, text=text)

start_probability = 0.8
stop_probability = 0.1
start_precipitation = 0.03
stop_precipitation = 0.005
rain_4h = rain_2h = rain_60 = rain_15 = rain_0 = False
newmsg = 0

def forecast_rain(bot):
    global newmsg

    # try:
    #     probability_4h = caiyunData['result']['minutely']['probability_4h']
    #     global rain_4h
    #     if max(probability_4h) < stop_probability and rain_4h == True:
    #         rain_4h = False
    #         logging.info('rain_4h T to F')
    #     if max(probability_4h) > start_probability and rain_4h == False:
    #         rain_4h = True
    #         bot.send_message(chat_id=group, text='未来四小时内可能会下雨。')
    #         logging.info('rain_4h F to T')
    # except:
    #     pass

    try:
        probability_2h = caiyunData['result']['minutely']['probability']
        # logging.info(probability_2h)
        global rain_2h
        if max(probability_2h) < stop_probability and rain_2h == True:
            rain_2h = False
            logging.info('rain_2h T to F')
        if max(probability_2h) > start_probability and rain_2h == False:
            rain_2h = True
            if newmsg > 0:
                bot.edit_message_text(chat_id=group, text='未来两小时内可能会下雨。', message_id=newmsg)
            else:
                newmsg = bot.send_message(chat_id=group, text='未来两小时内可能会下雨。').message_id
            logging.info('rain_2h F to T')
    except Exception as e:
        logging.error(e)

    global rain_60, rain_15, rain_0
    changed = False
    precipitation = caiyunData['result']['minutely']['precipitation_2h']
    if (precipitation[60] < stop_precipitation and rain_60 == True) or (precipitation[60] > start_precipitation and rain_60 == False):
        rain_60 = not rain_60
        changed = True
    if (precipitation[15] < stop_precipitation and rain_15 == True) or (precipitation[15] > start_precipitation and rain_15 == False):
        rain_15 = not rain_15
        changed = True
    if (precipitation[0] < stop_precipitation and rain_0 == True) or (precipitation[0] > start_precipitation and rain_0 == False):
        rain_0 = not rain_0
        changed = True
    # logging.info((precipitation[0], precipitation[15], precipitation[60], rain_0, rain_15, rain_60))

    if changed:
        if newmsg > 0:
            bot.edit_message_text(chat_id=group, text=caiyunData['result']['forecast_keypoint'], message_id=newmsg)
        else:
            newmsg = bot.send_message(chat_id=group, text=caiyunData['result']['forecast_keypoint']).message_id

caiyunFailedCount = 0

def caiyun(bot, job):

    global caiyunData, caiyunFailedCount
    try:
        caiyunData = json.loads(crawler.request('https://api.caiyunapp.com/v2/{}/{},{}/weather.json?lang=zh_CN' \
            .format(config['CAIYUN']['token'], config['CAIYUN']['longitude'], config['CAIYUN']['latitude'])))

        assert caiyunData['status'] == 'ok'

        with open('data/caiyun.json', 'w') as file:
            json.dump(caiyunData, file)

        caiyunFailedCount = 0

    except:
        logging.warning('Failed to get data from CaiYun.')
        caiyunFailedCount += 1
        if caiyunFailedCount == 5:
            bot.send_message(chat_id=owner, text='Failed to get data from CaiYun 5 times.')
        return

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

    logging.info('\\weather_thu {}'.format(update.message.chat_id))

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
connected = False

def connectSocket():

    mainSocket = socket(AF_INET,SOCK_STREAM)
    mainSocket.bind((config['SERVER']['ip'], config['SERVER'].getint('port')))
    mainSocket.listen(1)

    global serverSocket, connected
    logging.info('Wait for connection...')
    connected = False
    serverSocket,destAdr = mainSocket.accept()
    serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
    logging.info('Connect establish!')
    connected = True

    global TESTSUC, info_UPDATE
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
            elif msg[0] == 'I':
                lock.acquire()
                try:
                    global newMessages
                    newMessages.extend(json.loads(msg[1:]))
                    info_UPDATE = True
                except Exception as e:
                    logging.error(e)
                lock.release()
                serverSocket.send('S'.encode('utf8'))
            elif msg[0] == 'D':
                lock.acquire()
                try:
                    global delMessages
                    delMessages.extend(json.loads(msg[1:]))
                    info_UPDATE = True
                except Exception as e:
                    logging.error(e)
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

preHour = time.localtime().tm_hour

def forecast_daily(bot, job):

    global preHour
    hour = time.localtime().tm_hour
    if preHour != hour:
        preHour = hour
        if hour == 6 or hour == 18:
            text = '天气：' + caiyunData['result']['hourly']['description'] + '\n当前状态：' + ('正常' if connected else '异常')
            bot.send_message(chat_id=group, text=text)
        elif hour == 23:
            text = 'Today Info:'
            global today_news, sended_news
            for source in today_news:
                text += '\n' + ' - %s' % source
                for news in today_news[source]:
                    text += '\n' + '[%s](%s)' % (news['title'], news['url'])
            today_news = {}
            sended_news = {}
            bot.send_message(chat_id=group,
                                text=text,
                                parse_mode='Markdown')

emoji = '👮🚔🚨🚓'

def callpolice(bot, update):

    logging.info('\\callpolice {}'.format(update.message.chat_id))
    random.seed(math.floor(time.time()))

    text = ''
    for i in range(random.randint(10, 100)):
        text += emoji[random.randint(0, 3)]
    bot.send_message(chat_id=update.message.chat_id, text=text)

def precipitation_graph():

    pic = 'pic/' + str(int(time.time())) + '.png'
    logging.info('\\precipitation_graph {}'.format(pic))

    if not os.path.exists('pic/'):
        os.makedirs('pic/')

    precipitation = caiyunData['result']['minutely']['precipitation_2h']
    plt.figure()
    plt.plot(np.arange(120), np.array(precipitation))
    
    plt.ylim(ymin = 0)
    if plt.axis()[3] > 0.03:
        plt.hlines(0.03, 0, 120, colors='skyblue', linestyles='dashed')
    if plt.axis()[3] > 0.25:
        plt.hlines(0.25, 0, 120, colors='blue', linestyles='dashed')
    if plt.axis()[3] > 0.35:
        plt.hlines(0.35, 0, 120, colors='orange', linestyles='dashed')
    if plt.axis()[3] > 0.48:
        plt.hlines(0.48, 0, 120, colors='darkred', linestyles='dashed')
        
    plt.title('precipitation in 2 hours')
    plt.savefig(pic)
    
    return pic

def new_message(bot, update):
    global newmsg
    newmsg = 0

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
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler('callpolice', callpolice))
    dp.add_handler(MessageHandler(Filters.text, new_message))

    updater.job_queue.run_repeating(info, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(rain_thu, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(caiyun, interval=60, first=0, context=group)
    updater.job_queue.run_repeating(forecast_daily, interval=10, first=0, context=group)

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    connect = Thread(target=connectSocket)
    connect.start()
    main()
