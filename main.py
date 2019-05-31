# -*- coding: utf-8 -*-
# @source: Konano
# @Date:   2019-05-28 14:12:29
# @Last Modified by:   NanoApe
# @Last Modified time: 2019-05-31 21:21:42

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

import configparser

config = configparser.ConfigParser()
config.read('config.ini')
owner = config['BOT'].getint('owner')
group = config['BOT'].getint('group')

running = False

def update_config():
    with open('config.ini', 'w') as configFile:
        config.write(configFile)

from telegram.ext import Updater, CommandHandler, Filters

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


import crawler
import json

with open('data/mute.json', 'r') as file:
    mute_list = json.load(file)

logging.info(mute_list)


def mute(bot, update, args):

    if update.message.chat_id != owner and update.message.chat_id != group:
        return
    logging.info('\\mute')

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
    logging.info('\\unmute')

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


def detect(bot, job):

    messages = []

    category_list = ['academic', '7days', 'business', 'poster', 'research']
    for category in category_list:
        messages += crawler.detect(config['URL'][category])

    messages += crawler.detectBoard(config['URL']['board'])

    try:
        with open('data/postinfo.json', 'r') as file:
            lastMessages = json.load(file)
    except:
        lastMessages = []

    newMessages = []

    for each in messages:
        if each['source'] not in mute_list:
            each['title'] = each['title'].replace('[','(').replace(']',')')
            if each['url'][0] == '/':
                each['url'] = config['URL']['postinfo'] + each['url']
            if each not in lastMessages:
                newMessages.append(each)

    if newMessages != []:
        logging.info('Detected new messages: ' + str(len(newMessages)))
        for each in newMessages:
            bot.send_message(chat_id=group,
                             text='Info %s\n[%s](%s)' % (each['source'], each['title'], each['url']),
                             parse_mode='Markdown')
    else:
        logging.info('Detected no new messages')

    with open('data/postinfo.json', 'w') as file:
        json.dump(messages, file)


def init(job_queue):

    job_queue.run_repeating(detect, interval=300, first=0)


def setid(bot, update):

    if update.message.chat_id > 0 or update.effective_user.id != owner:
        return
    logging.info('\\setid')

    group = update.message.chat_id
    config['BOT']['group'] = str(group)
    update_config()


def main():

    updater = Updater(config['BOT']['accesstoken'], request_kwargs={'proxy_url': config['BOT']['socks5']})

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('mute', mute, pass_args=True))
    dp.add_handler(CommandHandler('unmute', unmute, pass_args=True))
    dp.add_handler(CommandHandler('setid', setid))

    init(updater.job_queue)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()