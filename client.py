# -*- coding: utf-8 -*-
# @Author: Konano
# @Date:   2019-06-16 17:20:10
# @Last Modified by:   Konano
# @Last Modified time: 2019-06-17 22:29:44

import crawler
import json
import time

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

from socket import *
from threading import Thread

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s',
                    # level=logging.INFO)
                    level=logging.INFO,
                    filename=config['CLIENT']['logfile'])
logger = logging.getLogger(__name__)


def detect():

    while True:

        messages = []

        try:
            category_list = ['academic', '7days', 'business', 'poster', 'research']
            for category in category_list:
                messages += crawler.detect(config['URL'][category])
            messages += crawler.detectBoard(config['URL']['board'])
        except:
            continue

        for each in messages:
            each['title'] = each['title'].replace('[','(').replace(']',')')
            if each['url'][0] == '/':
                each['url'] = config['URL']['postinfo'] + each['url']

        try:
            with open('data/postinfo.json', 'r') as file:
                lastMessages = json.load(file)
        except:
            lastMessages = []

        newMessages = []

        for each in messages:
            if each not in lastMessages:
                newMessages.append(each)

        logging.info('Messages: %d, New: %d'%(len(messages),len(newMessages)))

        if len(newMessages) > 0 and len(newMessages) < 10:
            try:
                clientSocket.send(json.dumps(newMessages).encode('utf8'))
            except:
                logging.exception('ConnectionError')
                return

        if abs(len(messages)-len(lastMessages)) < 10:
            with open('data/postinfo.json', 'w') as file:
                json.dump(messages, file)
        else:
            logging.warnning('not Save')

        time.sleep(60)

def main():

    global running, clientSocket

    while True:
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM)
            clientSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
            clientSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
            clientSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
            clientSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
            clientSocket.connect((config['CLIENT']['ip'], config['CLIENT'].getint('port')))
            logging.info('Connect establish!')
        except:
            logging.exception('ConnectionError')
            time.sleep(60)
            continue

        detect()
        clientSocket.close()


if __name__ == '__main__':
    main()