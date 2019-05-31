# -*- coding: utf-8 -*-
# @source: NanoApe
# @Date:   2019-05-24 22:35:35
# @Last Modified by:   NanoApe
# @Last Modified time: 2019-05-31 20:47:28

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