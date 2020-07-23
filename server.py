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
import configparser
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler


# Connect

connectTimeLimit = 10

class InvalidParameter(Exception):
    """Invalid Parameter"""

class ConnectError(Exception):
    """Connect Error"""

class ConnectTimeout(Exception):
    """Connect Timeout"""


# Config

config = configparser.ConfigParser()
config.read('config.ini')
owner = config['BOT'].getint('owner')
group = config['BOT'].getint('group')
channel = config['BOT'].getint('channel')
pipe = config['BOT'].getint('pipe')

def update_config():
    with open('config.ini', 'w') as configFile:
        config.write(configFile)


# Log

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s',
                    level=logging.INFO)
                    # level=logging.INFO,
                    # filename=config['BOT']['log'])
logger = logging.getLogger(__name__)


def help(update, context):
    logging.info('\\help')
    text = '''
可用：

/weather - 显示当前位置的天气（彩云）
/forecast - 降雨分钟级预报
/forecast_hourly - 天气小时级预报
/mute - 屏蔽发布源
/unmute - 解除屏蔽发布源
/mute_list - 列出所有被屏蔽的发布源
/roll - 从 1 开始的随机数
/callpolice - 在线报警
/status - Bot 连接状态
/help - 可用指令说明

废弃：

/libseat - 查看文图座位剩余情况
/weather_thu - 显示学校区域当前的天气（学校天气站）
/weather_today - 显示当前位置的今日天气预报（彩云）
'''
    context.bot.send_message(owner, text)


# MarkdownV2 Mode

def escaped(str):
    return re.sub('([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])', '\\\\\\1', str)


# WebVPN

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


def roll(update, context):

    logging.info('\\roll ' + json.dumps(context.args))

    try:
        random.seed(math.floor(time.time()))
        context.bot.send_message(owner, 'Choose: '+str(random.randint(1,int(context.args[0]))))
    except:
        context.bot.send_message(owner, 'Usage: /roll [total]')

# Info

lock = Lock()
newMessages = []
delMessages = []
INFO_UPDATE = False
today_news = {}
sended_news = {}
urls = {}

def info(update, context):

    try:
        rev = json.loads(update.channel_post.text)
        logging.info(rev)
        data = rev[data]
        if rev['type'] == 'newinfo':
            urls[data['url']] = data
            if data['source'] not in today_news:
                today_news[data['source']] = []
            today_news[data['source']].append(data)
            if data['source'] not in muted:
                text = 'Info %s\n[%s](%s) [\\(webvpn\\)](%s)' % (escaped(data['source']), escaped(data['title']), data['url'], webvpn(data['url']))
                msg = context.bot.send_message(chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
                sended_news[data['url']] = msg.message_id

        elif rev['type'] == 'delinfo':
            if data in sended_news:
                context.bot.delete_message(chat_id=group, message_id=sended_news[data])
                del sended_news[data]
            if data in urls.keys() and urls[data]['source'] in today_news and urls[data] in today_news[each['source']]:
                today_news[urls[data]['source']].remove(urls[data])
                if today_news[urls[data]['source']] == []:
                    del today_news[urls[data]['source']]

    except Exception as e:
        logging.error(e)

# def info(context):

#     global newMessages, delMessages, INFO_UPDATE, today_news, sended_news

#     if INFO_UPDATE == False:
#         return
#     INFO_UPDATE = False

#     lock.acquire()

#     try:
#         for each in newMessages:
#             if each['source'] not in today_news:
#                 today_news[each['source']] = []
#             today_news[each['source']].append(each)

#         if delMessages != []:
#             logging.info('Detected del messages: ' + str(len(delMessages)))
#             for each in delMessages:
#                 if each['url'] in sended_news:
#                     context.bot.delete_message(
#                         chat_id=group,
#                         message_id=sended_news[each['url']])
#                     del sended_news[each['url']]
#                 if each['source'] in today_news and each in today_news[each['source']]:
#                     today_news[each['source']].remove(each)
#                     if today_news[each['source']] == []:
#                         del today_news[each['source']]

#         # for each in newMessages:
#         #     text = 'Info %s\n[%s](%s) [\\(webvpn\\)](%s)' % (escaped(each['source']), escaped(each['title']), each['url'], webvpn(each['url']))
#         #     context.bot.send_message(chat_id=channel, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)

#         newMessages = [each for each in newMessages if each['source'] not in muted]

#         if newMessages != []:
#             logging.info('Detected new messages: ' + str(len(newMessages)))
#             for each in newMessages:
#                 text = 'Info %s\n[%s](%s) [\\(webvpn\\)](%s)' % (escaped(each['source']), escaped(each['title']), each['url'], webvpn(each['url']))
#                 msg = context.bot.send_message(chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
#                 sended_news[each['url']] = msg.message_id
#     except Exception as e:
#         logging.error(e)
        
#     newMessages = []
#     delMessages = []

#     lock.release()


"""
RAIN_UPDATE = 0

def rain_thu(bot, job):

    global RAIN_UPDATE

    if RAIN_UPDATE == 0:
        return

    try:
        if RAIN_UPDATE == +1:
            context.bot.send_message(chat_id=group, text='下雨了。')
        elif RAIN_UPDATE == -1:
            context.bot.send_message(chat_id=group, text='雨停了。')
    except Exception as e:
        logging.error(e)

    RAIN_UPDATE = 0
"""


# Caiyun

def deal_precipitation(str):

    intensity = float(str)
    if intensity == 0: return '无'
    elif intensity < 0.031: return '毛毛雨'
    elif intensity < 0.25: return '小雨'
    elif intensity < 0.35: return '中雨'
    elif intensity < 0.48: return '大雨'
    else: return '暴雨'

def deal_skycon(str):

    switch = {
        'CLEAR_DAY': '晴',
        'CLEAR_NIGHT': '晴',
        'PARTLY_CLOUDY_DAY': '多云',
        'PARTLY_CLOUDY_NIGHT': '多云',
        'CLOUDY': '阴',
        'LIGHT_HAZE': '轻度雾霾',
        'MODERATE_HAZE': '中度雾霾',
        'HEAVY_HAZE': '重度雾霾',
        'HAZE': '雾霾',
        'LIGHT_RAIN': '小雨',
        'MODERATE_RAIN': '中雨',
        'HEAVY_RAIN': '大雨',
        'STORM_RAIN': '暴雨',
        'RAIN': '雨',
        'FOG': '雾',
        'LIGHT_SNOW': '小雪',
        'MODERATE_SNOW': '中雪',
        'HEAVY_SNOW': '大雪',
        'STORM_SNOW': '暴雪',
        'SNOW': '雪',
        'WIND': '大风',
        'DUST': '浮尘',
        'SAND': '沙尘',
        'THUNDER_SHOWER': '雷阵雨',
        'HAIL': '冰雹',
        'SLEET': '雨夹雪'
    }
    try:
        return switch[str]
    except KeyError as e:
        return str

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

def dir_diff(a, b):
    c = a - b
    if c > 180:
        c -= 360
    if c < -180:
        c += 360
    return c

def dir_diff_abs(a, b):
    if a < b:
        a, b = b, a
    return min(a - b, 360 - (a - b))

def wind_direction(str):

    dir = float(str)
    dir_val = [0, 45, 90, 135, 180, 225, 270, 315]
    dir_desc = ['正北', '东北', '正东', '东南', '正南', '西南', '正西', '西北']
    dir_bias = ['西东', '北东', '北南', '东南', '东西', '南西', '南北', '西北']

    main_dir = 0
    for i in range(1, 8):
        if dir_diff_abs(dir, dir_val[i]) < dir_diff_abs(dir, dir_val[main_dir]):
            main_dir = i
    str = dir_desc[main_dir]
    if dir_diff(dir, dir_val[main_dir]) < 0:
        str += '偏' + dir_bias[main_dir][:1]
    else:
        str += '偏' + dir_bias[main_dir][-1:]
    return str

def alert_type(str):
    
    switchA = {
        '01': '台风',
        '02': '暴雨',
        '03': '暴雪',
        '04': '寒潮',
        '05': '大风',
        '06': '沙尘暴',
        '07': '高温',
        '08': '干旱',
        '09': '雷电',
        '10': '冰雹',
        '11': '霜冻',
        '12': '大雾',
        '13': '霾',
        '14': '道路结冰',
        '15': '森林火灾',
        '16': '雷雨大风'
    }
    switchB = {
        '01': '蓝色预警',
        '02': '黄色预警',
        '03': '橙色预警',
        '04': '红色预警'
    }

    try:
        return switchA[str[:2]] + switchB[str[-2:]]
    except KeyError as e:
        return str + '(UnknownCode)'

def alert_now():

    alerts = []
    if caiyunData['result']['alert']['status'] == 'ok':
        for each in caiyunData['result']['alert']['content']:
            if each['request_status'] == 'ok':
                alerts.append(alert_type(each['code']))
    return alerts

def caiyun_temp_min():
    temp_min = 999.99
    for i in range(12):
        temp_min = min(temp_min, float(caiyunData['result']['hourly']['temperature'][i]['value']))
    return temp_min

def caiyun_temp_max():
    temp_max = -999.99
    for i in range(12):
        temp_max = max(temp_max, float(caiyunData['result']['hourly']['temperature'][i]['value']))
    return temp_max

def caiyun_humi_avg():
    humi_avg = 0.0
    for i in range(12):
        humi_avg += float(caiyunData['result']['hourly']['humidity'][i]['value'])
    return round(humi_avg / 12, 2)

def caiyun_wind_avg():
    wind_avg = 0.0
    for i in range(12):
        wind_avg += float(caiyunData['result']['hourly']['wind'][i]['speed'])
    return round(wind_avg / 12, 1)

def caiyun_visi_avg():
    visi_avg = 0.0
    for i in range(12):
        visi_avg += float(caiyunData['result']['hourly']['visibility'][i]['value'])
    return round(visi_avg / 12, 2)

def caiyun_aqi_avg():
    aqi_avg = 0.0
    for i in range(12):
        aqi_avg += float(caiyunData['result']['hourly']['air_quality']['aqi'][i]['value']['chn'])
    return int(aqi_avg / 12)

def daily_weather(dayornight):

    if dayornight == 'day':
        return \
            '天气：{}\n'.format(caiyunData['result']['hourly']['description']) + \
            '温度：{}~{}℃\n'.format(caiyun_temp_min(), caiyun_temp_max()) + \
            '湿度：{}%\n'.format(int(caiyun_humi_avg()*100)) + \
            '风速：{}m/s ({})\n'.format(caiyun_wind_avg(), level_windspeed(caiyun_wind_avg())) + \
            '能见度：{}km\n'.format(caiyun_visi_avg()) + \
            '今日日出：{}\n'.format(caiyunData['result']['daily']['astro'][0]['sunrise']['time']) + \
            '今日日落：{}\n'.format(caiyunData['result']['daily']['astro'][0]['sunset']['time']) + \
            'AQI：{}\n'.format(caiyun_aqi_avg()) + \
            '紫外线：{}\n'.format(caiyunData['result']['daily']['life_index']['ultraviolet'][0]['desc']) + \
            '舒适度：{}\n'.format(caiyunData['result']['daily']['life_index']['comfort'][0]['desc']) + \
            ('现挂预警信号：{}\n'.format(' '.join(alert_now())) if alert_now() != [] else '')
    else:
        return \
            '天气：{}\n'.format(caiyunData['result']['hourly']['description']) + \
            '温度：{}~{}℃\n'.format(caiyun_temp_min(), caiyun_temp_max()) + \
            '湿度：{}%\n'.format(int(caiyun_humi_avg()*100)) + \
            '风速：{}m/s ({})\n'.format(caiyun_wind_avg(), level_windspeed(caiyun_wind_avg())) + \
            '能见度：{}km\n'.format(caiyun_visi_avg()) + \
            '明日日出：{}\n'.format(caiyunData['result']['daily']['astro'][1]['sunrise']['time']) + \
            '明日日落：{}\n'.format(caiyunData['result']['daily']['astro'][1]['sunset']['time']) + \
            'AQI：{}\n'.format(caiyun_aqi_avg()) + \
            ('现挂预警信号：{}\n'.format(' '.join(alert_now())) if alert_now() != [] else '')

# def weather_today(update, context):

#     logging.info('\\weather_today')

#     assert caiyunData['result']['hourly']['status'] == 'ok'
#     assert caiyunData['result']['daily']['status'] == 'ok'

#     text = \
#         '清华今日天气：{}\n'.format(caiyunData['result']['hourly']['description']) + \
#         '温度：{}~{}℃\n'.format(caiyunData['result']['daily']['temperature'][0]['min'], caiyunData['result']['daily']['temperature'][0]['max']) + \
#         '湿度：{}%\n'.format(int(float(caiyunData['result']['daily']['humidity'][0]['avg'])*100)) + \
#         '风速：{}m/s ({})\n'.format(caiyunData['result']['daily']['wind'][0]["avg"]['speed'], level_windspeed(caiyunData['result']['daily']['wind'][0]["avg"]['speed'])) + \
#         '能见度：{}km\n'.format(caiyunData['result']['daily']['visibility'][0]['avg']) + \
#         '日出：{}\n'.format(caiyunData['result']['daily']['astro'][0]['sunrise']['time']) + \
#         '日落：{}\n'.format(caiyunData['result']['daily']['astro'][0]['sunset']['time']) + \
#         'AQI：{}\n'.format(caiyunData['result']['daily']['air_quality']['aqi'][0]['avg']['chn']) + \
#         '紫外线：{}\n'.format(caiyunData['result']['daily']['life_index']['ultraviolet'][0]['desc']) + \
#         '舒适度：{}\n'.format(caiyunData['result']['daily']['life_index']['comfort'][0]['desc']) + \
#         ('现挂预警信号：{}\n'.format(' '.join(alert_now())) if alert_now() != [] else '')

#     context.bot.send_message(chat_id=update.message.chat_id, text=text)

def precipitation_graph():

    pic = 'pic/' + str(int(time.time())) + '.png'
    logging.info('\\precipitation_graph {}'.format(pic))

    if not os.path.exists('pic/'):
        os.makedirs('pic/')

    precipitation = caiyunData['result']['minutely']['precipitation_2h']
    plt.figure(figsize=(6,3))
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

def forecast(update, context):

    logging.info('\\forecast {}'.format(update.message.chat_id))

    pic = precipitation_graph()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(pic, 'rb'), caption=caiyunData['result']['forecast_keypoint'])

def forecast_hourly(update, context):

    logging.info('\\forecast_hourly {}'.format(update.message.chat_id))

    context.bot.send_message(chat_id=update.message.chat_id, text=caiyunData['result']['hourly']['description'])

def weather(update, context):

    logging.info('\\weather {}'.format(update.message.chat_id))

    assert caiyunData['result']['realtime']['status'] == 'ok'

    text = ''
    text += '清华当前天气：{}\n'.format(deal_skycon(caiyunData['result']['realtime']['skycon']))
    text += '温度：{}℃\n'.format(caiyunData['result']['realtime']['temperature'])
    if 'apparent_temperature' in caiyunData['result']['realtime']:
        text += '体感：{}℃\n'.format(caiyunData['result']['realtime']['apparent_temperature'])
    text += '湿度：{}%\n'.format(int(float(caiyunData['result']['realtime']['humidity'])*100))
    text += '风向：{}\n'.format(wind_direction(caiyunData['result']['realtime']['wind']['direction']))
    text += '风速：{}m/s ({})\n'.format(caiyunData['result']['realtime']['wind']['speed'], level_windspeed(caiyunData['result']['realtime']['wind']['speed']))
    if caiyunData['result']['realtime']['precipitation']['local']['status'] == 'ok':
        text += '降水：{}\n'.format(deal_precipitation(caiyunData['result']['realtime']['precipitation']['local']['intensity']))
    text += '能见度：{}km\n'.format(caiyunData['result']['realtime']['visibility'])
    text += 'PM2.5：{}\n'.format(caiyunData['result']['realtime']['air_quality']['pm25'])
    text += 'AQI：{} ({})\n'.format(caiyunData['result']['realtime']['air_quality']['aqi']['chn'], caiyunData['result']['realtime']['air_quality']['description']['chn'])
    text += '紫外线：{}\n'.format(caiyunData['result']['realtime']['life_index']['ultraviolet']['desc'])
    text += '舒适度：{}\n'.format(caiyunData['result']['realtime']['life_index']['comfort']['desc'])
    if alert_now() != []:
        text += '现挂预警信号：{}\n'.format(' '.join(alert_now()))

    context.bot.send_message(chat_id=update.message.chat_id, text=text)

start_probability = 0.8
stop_probability = 0.1
start_precipitation = 0.03
stop_precipitation = 0.005
rain_2h = rain_60 = rain_15 = rain_0 = False
newmsg = 0

def forecast_rain(bot):

    global newmsg
    assert caiyunData['result']['minutely']['status'] == 'ok'

    probability_2h = caiyunData['result']['minutely']['probability']
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

    if changed:
        if newmsg > 0:
            bot.edit_message_text(chat_id=group, text=caiyunData['result']['forecast_keypoint'], message_id=newmsg)
        else:
            newmsg = bot.send_message(chat_id=group, text=caiyunData['result']['forecast_keypoint']).message_id

caiyunFailedCount = 0
alerts = {}

def caiyun(context):

    global caiyunData, caiyunFailedCount
    try:
        caiyunData = json.loads(crawler.request('https://api.caiyunapp.com/v2.5/{}/{},{}/weather.json?lang=zh_CN&alert=true' \
            .format(config['CAIYUN']['token'], config['CAIYUN']['longitude'], config['CAIYUN']['latitude'])))

        assert caiyunData['status'] == 'ok'

        with open('data/caiyun.json', 'w') as file:
            json.dump(caiyunData, file)

        caiyunFailedCount = 0

    except:
        logging.warning('Failed to get data from CaiYun.')
        caiyunFailedCount += 1
        if caiyunFailedCount == 5:
            context.bot.send_message(chat_id=owner, text='Failed to get data from CaiYun 5 times.')
        return

    forecast_rain(context.bot)

    if caiyunData['result']['alert']['status'] == 'ok':
        for each in caiyunData['result']['alert']['content']:
            if each['request_status'] == 'ok' and each['alertId'] not in alerts:
                context.bot.send_message(chat_id=group,   text='*{}*\n\n{}'.format(escaped(each['title']), escaped(each['description'])), parse_mode='MarkdownV2')
                context.bot.send_message(chat_id=channel, text='*{}*\n\n{}'.format(escaped(each['title']), escaped(each['description'])), parse_mode='MarkdownV2')
                alerts[each['alertId']] = each


# Info Mute

with open('data/mute.json', 'r') as file:
    muted = json.load(file)

def mute(update, context):

    logging.info('\\mute ' + json.dumps(context.args))

    if context.args == []:
        context.bot.send_message(owner, 'Usage: /mute [source]')
        return

    global muted
    for each in context.args:
        if each not in muted:
            muted.append(each)

    with open('data/mute.json', 'w') as file:
        json.dump(muted, file)

    context.bot.send_message(update.message.chat_id, 'Muted: ' + ' '.join(context.args))

def unmute(update, context):

    logging.info('\\unmute ' + json.dumps(context.args))

    if context.args == []:
        context.bot.send_message(update.message.chat_id, 'Usage: /unmute [source]')
        return

    global muted
    for each in context.args:
        muted.remove(each)

    with open('data/mute.json', 'w') as file:
        json.dump(muted, file)

    context.bot.send_message(update.message.chat_id, 'Unmuted: ' + ' '.join(context.args))

def mute_show(update, context):

    logging.info('\\mute_list')

    text = 'Muted list:'
    for each in muted:
        text += '\n' + each

    context.bot.send_message(update.message.chat_id, text)


# Weather in THU

# WEATHER_THU_REQUEST = False
# WEATHER_THU_DATA = {}

# def weather_thu(update, context):

#     logging.info('\\weather_thu {}'.format(update.message.chat_id))

#     try:
#         global serverSocket
#         serverSocket.send('W'.encode('utf8'))
#         logging.info('Send request')
#     except:
#         logging.exception('Connect Error')
#         return

#     try:
#         global WEATHER_THU_REQUEST
#         WEATHER_THU_REQUEST = True
#         cnt = 10 * connectTimeLimit
#         while WEATHER_THU_REQUEST:
#             time.sleep(0.1)
#             cnt -= 1
#             if cnt <= 0:
#                 raise
#     except:
#         context.bot.send_message(update.message.chat_id, 'Time out: %ds'%connectTimeLimit)
#         logging.warning('Don\'t receive any data in %ds'%connectTimeLimit)
#         return

#     logging.info('Received data')
#     text = ''
#     for station in WEATHER_THU_DATA:
#         if text != '':
#             text += '\n'
#         text += station['location'] + '\n'
#         text += station['date'] + ' ' + station['time'] + '\n'
#         text += '{}℃  {}%  {}m/s  {}mm\n'.format(station['temperature'], station['humidity'], station['wind_speed'], station['rainfall_10mins'])
#     context.bot.send_message(update.message.chat_id, text)


# Daily report

preHour = time.localtime().tm_hour

def daily_report(context):

    global preHour
    hour = time.localtime().tm_hour
    if preHour != hour:
        preHour = hour
        if hour == 6 or hour == 18:
            text = daily_weather('day' if hour == 6 else 'night') + '当前状态：' + ('正常' if connectStatus else '异常')
            context.bot.send_message(chat_id=group,   text=text)
            context.bot.send_message(chat_id=channel, text=text)
        elif hour == 23:
            text = 'Today Info:'
            global today_news, sended_news
            for source in today_news:
                text += '\n \\- %s' % escaped(source)
                for news in today_news[source]:
                    text += '\n[%s](%s)' % (escaped(news['title']), news['url'])
            today_news = {}
            sended_news = {}
            context.bot.send_message(chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)


# Call Police

emoji = '👮🚔🚨🚓'

def callpolice(update, context):

    logging.info('\\callpolice {}'.format(update.message.chat_id))
    random.seed(math.floor(time.time()))

    text = ''
    for i in range(random.randint(10, 100)):
        text += emoji[random.randint(0, 3)]
    context.bot.send_message(chat_id=update.message.chat_id, text=text)


# New Message

def new_message(update, context):
    global newmsg
    newmsg = 0


# Connect

TRANSFER_SUCC = 0
connectStatus = True # FIXME connectStatus should be False

def connectSocket():

    mainSocket = socket(AF_INET,SOCK_STREAM)
    mainSocket.bind((config['SERVER']['ip'], config['SERVER'].getint('port')))
    mainSocket.listen(1)

    global serverSocket, connectStatus
    logging.info('Wait for connection...')
    connectStatus = False
    serverSocket,destAdr = mainSocket.accept()
    serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
    serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
    logging.info('Connect establish!')
    connectStatus = True

    global TRANSFER_SUCC, INFO_UPDATE
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
                    TRANSFER_SUCC += 1
                    if TRANSFER_SUCC % 10 == 0:
                        logging.info('TRANSFER_SUCC * 10')
                    continue

            logging.info(msg)
            if msg == '':
                raise
            if msg[0] == 'W':     # weather
                global WEATHER_THU_REQUEST, WEATHER_THU_DATA
                WEATHER_THU_DATA = json.loads(msg[1:])
                WEATHER_THU_REQUEST = False
                serverSocket.send('S'.encode('utf8'))
            # elif msg[0] == 'R':
            #     logging.info(msg)
            #     global RAIN_UPDATE
            #     if msg[1] == 'S':
            #         RAIN_UPDATE = +1
            #     elif msg[1] == 'E':
            #         RAIN_UPDATE = -1
            #     serverSocket.send('S'.encode('utf8'))
            elif msg[0] == 'I':
                lock.acquire()
                try:
                    global newMessages
                    newMessages.extend(json.loads(msg[1:]))
                    INFO_UPDATE = True
                except Exception as e:
                    logging.error(e)
                lock.release()
                serverSocket.send('S'.encode('utf8'))
            elif msg[0] == 'D':
                lock.acquire()
                try:
                    global delMessages
                    delMessages.extend(json.loads(msg[1:]))
                    INFO_UPDATE = True
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


# Status

def status(update, context):
    logging.info('\\status')
    text = '当前状态：' + ('正常' if connectStatus else '异常')
    context.bot.send_message(owner, text)


# Error Callback

def error_callback(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():

    if config['BOT'].getboolean('proxy'):
        updater = Updater(config['BOT']['accesstoken'], use_context=True, request_kwargs={'proxy_url': config['BOT']['socks5']})
    else:
        updater = Updater(config['BOT']['accesstoken'], use_context=True)

    dp = updater.dispatcher

    f_owner = Filters.chat(owner)
    f_group = Filters.chat(group)
    f_pipe = Filters.chat(pipe)

    dp.add_handler(CommandHandler('mute', mute, pass_args=True, filters=(f_owner|f_group)))
    dp.add_handler(CommandHandler('unmute', unmute, pass_args=True, filters=(f_owner|f_group)))
    dp.add_handler(CommandHandler('mute_list', mute_show, filters=(f_owner|f_group)))
    dp.add_handler(CommandHandler('forecast', forecast))
    dp.add_handler(CommandHandler('forecast_hourly', forecast_hourly))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler('roll', roll, pass_args=True))
    # dp.add_handler(CommandHandler('weather_thu', weather_thu))
    # dp.add_handler(CommandHandler('weather_today', weather_today))
    dp.add_handler(CommandHandler('callpolice', callpolice))
    dp.add_handler(CommandHandler('status', status, filters=f_owner))
    dp.add_handler(CommandHandler('help', help, filters=f_owner))

    dp.add_handler(MessageHandler(f_group & Filters.text, new_message))
    dp.add_handler(MessageHandler(f_pipe & Filters.update.channel_post, info))

    # updater.job_queue.run_repeating(info, interval=10, first=0, context=group)
    # updater.job_queue.run_repeating(rain_thu, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(caiyun, interval=60, first=0, context=group)
    updater.job_queue.run_repeating(daily_report, interval=10, first=0, context=group)

    dp.add_error_handler(error_callback)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    # connect = Thread(target=connectSocket)
    # connect.start()
    main()
