import json

from utils.log import logger
from utils.format import escaped
from utils.webvpn import webvpn
from utils.config import group
import utils.mute as mt

newMessages = []
delMessages = []
INFO_UPDATE = False
today_news = {}
sended_news = {}
urls = {}


def info(update, context): # TODO

    try:
        rev = json.loads(update.channel_post.text)
        logger.info(rev)
        data = rev['data']
        if rev['type'] == 'newinfo':
            urls[data['url']] = data
            if data['source'] not in today_news:
                today_news[data['source']] = []
            today_news[data['source']].append(data)
            if data['source'] not in mt.muted:
                text = 'Info %s\n[%s](%s) [\\(webvpn\\)](%s)' % (escaped(
                    data['source']), escaped(data['title']), data['url'], webvpn(data['url']))
                msg = context.bot.send_message(
                    chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
                sended_news[data['url']] = msg.message_id

        elif rev['type'] == 'delinfo':
            if data in sended_news:
                context.bot.delete_message(
                    chat_id=group, message_id=sended_news[data])
                del sended_news[data]
            if data in urls.keys() and urls[data]['source'] in today_news and urls[data] in today_news[urls[data]['source']]:
                today_news[urls[data]['source']].remove(urls[data])
                if today_news[urls[data]['source']] == []:
                    del today_news[urls[data]['source']]

    except Exception as e:
        logger.error(e)
