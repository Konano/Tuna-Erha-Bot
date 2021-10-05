import json
import traceback

from utils.log import logger
from utils.format import escaped
from utils.webvpn import webvpn
from utils.config import group
import utils.mute as mt

try:
    with open('data/today.json', 'r') as file:
        today = json.load(file)
except:
    today = {}


def info(update, context):

    try:
        rev = json.loads(update.channel_post.text)
        logger.info(rev)
        data = rev['data']
        url = data['url']

        if rev['type'] == 'newinfo':
            today[url] = data
            today[url]['msgid'] = None
            if data['source'] not in mt.muted:
                text = 'Info %s\n[%s](%s) [\\(webvpn\\)](%s)' % (escaped(
                    data['source']), escaped(data['title']), data['url'], webvpn(data['url']))
                msg = context.bot.send_message(
                    chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
                today[url]['msgid'] = msg.message_id

        elif rev['type'] == 'delinfo':
            if url in today.keys():
                if today[url]['msgid'] is not None:
                    context.bot.delete_message(
                        chat_id=group, message_id=today[url]['msgid'])
                del today[url]
        
        with open('data/today.json', 'w') as file:
            json.dump(today, file)

    except Exception as e:
        logger.error(e)
        logger.debug(traceback.format_exc())


def info_daily(clear=True):
    ret = {}
    for info in today.values():
        if info['source'] not in ret.keys():
            ret[info['source']] = []
        ret[info['source']].append(info)
    if clear:
        today.clear()
        with open('data/today.json', 'w') as file:
            json.dump(today, file)
    return ret
