import time
from utils.caiyun import daily_weather
from utils.config import group, channel
from utils.format import escaped
import utils.connect as ct

preHour = time.localtime().tm_hour


def daily_report(context):

    global preHour
    hour = time.localtime().tm_hour
    if preHour != hour:
        preHour = hour
        if hour == 6 or hour == 18:
            text = daily_weather('day' if hour == 6 else 'night') + \
                '当前状态：' + ('正常' if ct.connectStatus else '异常')
            context.bot.send_message(chat_id=group,   text=text)
            context.bot.send_message(chat_id=channel, text=text)
        elif hour == 23:
            text = 'Today Info:'
            global today_news, sended_news
            for source in today_news:
                text += '\n \\- %s' % escaped(source)
                for news in today_news[source]:
                    text += '\n[%s](%s)' % (escaped(news['title']),
                                            news['url'])
            today_news = {}
            sended_news = {}
            context.bot.send_message(
                chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
