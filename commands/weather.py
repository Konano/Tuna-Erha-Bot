import utils.caiyun as cy
from utils.caiyun import deal_skycon, wind_direction, deal_precipitation, level_windspeed, alert_now
from utils.log import logger
import matplotlib.pyplot as plt
import time
import os
import traceback
import numpy as np
import matplotlib
matplotlib.use('Agg')


def precipitation_graph():

    pic = f'pic/{int(time.time())}.png'
    logger.info(f'\\precipitation_graph {pic}')

    try:
        if not os.path.exists('pic/'):
            os.makedirs('pic/')

        precipitation = cy.caiyunData['result']['minutely']['precipitation_2h']
        plt.figure(figsize=(6,3))
        plt.plot(np.arange(120), np.array(precipitation))
        plt.ylim(bottom = 0)
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
        plt.close('all')
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug(cy.caiyunData)
        logger.error(e)

    return pic


def forecast(update, context):

    logger.info('\\forecast {}'.format(update.message.chat_id))

    pic = precipitation_graph()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open(
        pic, 'rb'), caption=cy.caiyunData['result']['forecast_keypoint'])


def forecast_hourly(update, context):

    logger.info('\\forecast_hourly {}'.format(update.message.chat_id))

    context.bot.send_message(chat_id=update.message.chat_id,
                             text=cy.caiyunData['result']['hourly']['description'])


def weather(update, context):

    logger.info('\\weather {}'.format(update.message.chat_id))

    assert cy.caiyunData['result']['realtime']['status'] == 'ok'

    text = ''
    text += '清华当前天气：{}\n'.format(deal_skycon(
        cy.caiyunData['result']['realtime']['skycon']))
    text += '温度：{}℃\n'.format(cy.caiyunData['result']
                              ['realtime']['temperature'])
    if 'apparent_temperature' in cy.caiyunData['result']['realtime']:
        text += '体感：{}℃\n'.format(cy.caiyunData['result']
                                  ['realtime']['apparent_temperature'])
    text += '湿度：{}%\n'.format(
        int(float(cy.caiyunData['result']['realtime']['humidity'])*100))
    text += '风向：{}\n'.format(wind_direction(
        cy.caiyunData['result']['realtime']['wind']['direction']))
    text += '风速：{}m/s ({})\n'.format(cy.caiyunData['result']['realtime']['wind']['speed'],
                                     level_windspeed(cy.caiyunData['result']['realtime']['wind']['speed']))
    if cy.caiyunData['result']['realtime']['precipitation']['local']['status'] == 'ok':
        text += '降水：{}\n'.format(deal_precipitation(
            cy.caiyunData['result']['realtime']['precipitation']['local']['intensity']))
    text += '能见度：{}km\n'.format(cy.caiyunData['result']
                                ['realtime']['visibility'])
    text += 'PM2.5：{}\n'.format(cy.caiyunData['result']
                                ['realtime']['air_quality']['pm25'])
    text += 'AQI：{} ({})\n'.format(cy.caiyunData['result']['realtime']['air_quality']['aqi']
                                   ['chn'], cy.caiyunData['result']['realtime']['air_quality']['description']['chn'])
    text += '紫外线：{}\n'.format(cy.caiyunData['result']
                              ['realtime']['life_index']['ultraviolet']['desc'])
    text += '舒适度：{}\n'.format(cy.caiyunData['result']
                              ['realtime']['life_index']['comfort']['desc'])
    if alert_now() != []:
        text += '现挂预警信号：{}\n'.format(' '.join(alert_now()))

    context.bot.send_message(chat_id=update.message.chat_id, text=text)
