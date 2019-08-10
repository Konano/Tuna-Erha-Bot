# -*- coding: utf-8 -*-
# @Author: Konano
# @Date:   2019-06-16 17:20:10
# @Last Modified by:   Konano
# @Last Modified time: 2019-08-10 11:04:24

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

SENDSUC = False
def sendMsg(msg):
    global SENDSUC
    SENDSUC = False

    clientSocket.send(msg.encode('utf8'))

    cnt = 5
    while cnt > 0 and SENDSUC == False:
        cnt -= 1
        time.sleep(1)

    if SENDSUC == False:
        raise
    else:
        logging.info('SENDSUC')

def recvMsg(clientSocket):

    clientSocket.settimeout(5)

    global running, SENDSUC
    while running:
        try:
            try:
                msg = clientSocket.recv(512).decode('utf8')
            except timeout:
                continue

            if msg[0] == 'T':
                clientSocket.send('T'.encode('utf8'))
            elif msg[0] == 'S':
                SENDSUC = True
            elif msg[0] == 'W':
                logging.info(msg)
                weather = Thread(target=sendMsg,args=('W'+json.dumps(crawler.weather(config['URL']['weather'])),))
                weather.start()
        except:
            logging.exception('Connect Error')
            running = False

def detect():

    global running

    try:
        with open('data/postinfo.json', 'r') as file:
            lastMessages = json.load(file)
    except:
        lastMessages = []

    while running:

        messages = []
        try:
            category_list = ['academic', '7days', 'business', 'poster', 'research']
            for category in category_list:
                messages += crawler.detect(config['URL'][category])
            messages += crawler.detectBoard(config['URL']['board'])
        except:
            logging.info('Network Error')
            time.sleep(60)
            continue

        for each in messages:
            each['title'] = each['title'].replace('[','(').replace(']',')')
            if each['url'][0] == '/':
                each['url'] = config['URL']['postinfo'] + each['url']

        if len(messages) == 0:
            logging.warning('empty messages')

        newMessages = []

        for each in messages:
            if each not in lastMessages:
                newMessages.append(each)

        if len(newMessages) > 0:
            logging.info('Messages: %d, New: %d'%(len(messages),len(newMessages)))

        if len(newMessages) > 3:
            newMessages = newMessages[:3]

        if newMessages != []:

            try:
                sendMsg(json.dumps(newMessages))
            except:
                logging.exception('Connect Error')
                running = False
                return

            for each in newMessages:
                lastMessages.append(each)

            with open('data/postinfo.json', 'w') as file:
                json.dump(lastMessages, file)

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
            logging.exception('Connect Error')
            time.sleep(60)
            continue

        running = True
        tr = Thread(target=recvMsg,args=(clientSocket,))
        dt = Thread(target=detect)
        tr.start()
        dt.start()
        tr.join()
        dt.join()
        clientSocket.close()


if __name__ == '__main__':
    main()