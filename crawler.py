# -*- coding: utf-8 -*-
# @source: NanoApe
# @Date:   2019-05-24 22:35:35
# @Last Modified by:   Konano
# @Last Modified time: 2019-08-15 02:34:24

import requests
from bs4 import BeautifulSoup
import re


def detect(URL):

    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    content = bs.select('.cont_list > li')

    messages = []

    for each in content:
        tmp = re.split('\xa0\xa0|\t\n', each.get_text().strip())
        messages.append({'title' : tmp[0],
                         'source': tmp[1][1:-1],
                         'data'  : tmp[2],
                         'url'   : each.find('a').get('href')})

    return messages


def detectBoard(URL):

    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    content = bs.select('table > tr > td > a')

    messages = []

    for each in content:
        messages.append({'title' : each.get('title'),
                         'source': '重要公告',
                         'url'   : each.get('href')})

    return messages


def detectLibrary(URL):

    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    content = bs.select('table > tbody > tr > td > a')

    messages = []

    for each in content:
        messages.append({'title' : each.get_text(),
                         'source': '图书馆公告',
                         'url'   : 'http://lib.tsinghua.edu.cn'+each.get('href')})

    return messages



def libseat(URL):
    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')
    content = bs.select('table > tr')

    result = []

    for each in content[3:-1]:
        result.append({'name'  : each.select('td')[0].get_text(),
                       'used'  : each.select('td')[1].get_text(),
                       'remain': each.select('td')[2].get_text()})
    return result

stationList = [2, 3, 4, 5, 7]

def weather(URL):
    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

    result = []

    for station in bs.select('table'):
        if int(station.select('p')[0].get_text().split(' ')[0][0]) in stationList:
            result.append({'ID'              : station.select('p')[0].get_text().split(' ')[0][0],
                           'location'        : station.select('p')[0].get_text().split(' ')[1],
                           'date'            : station.select('p')[0].get_text().split(' ')[3],
                           'time'            : station.select('p')[0].get_text().split(' ')[4],
                           'temperature'     : station.select('tr')[1].select('td')[1].get_text(),
                           'wind_direction'  : station.select('tr')[1].select('td')[3].get_text(),
                           'humidity'        : station.select('tr')[2].select('td')[1].get_text(),
                           'wind_speed'      : station.select('tr')[2].select('td')[3].get_text(),
                           'rainfall_10mins' : station.select('tr')[3].select('td')[1].get_text(),
                           'hPa'             : station.select('tr')[3].select('td')[3].get_text()})
    return result

def rainfall(URL):
    html = requests.get(URL).content
    bs = BeautifulSoup(html, 'lxml', from_encoding='utf-8')

    maxRainfall = 0.0

    for station in bs.select('table'):
        if int(station.select('p')[0].get_text().split(' ')[0][0]) in stationList:
            maxRainfall = max(maxRainfall, float(station.select('tr')[3].select('td')[1].get_text()))

    return maxRainfall

def request(URL):

    return requests.get(URL, timeout=(5,10)).content.decode('utf-8')
