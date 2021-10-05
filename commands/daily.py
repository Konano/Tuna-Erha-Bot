from utils.caiyun import daily_weather
from utils.config import group, channel
from utils.format import escaped
import commands.info as info


def weather_report(context):
    text = daily_weather(context.job.context)
    context.bot.send_message(chat_id=group,   text=text)
    context.bot.send_message(chat_id=channel, text=text)


def daily_report(context):
    text = 'Today Info:'
    for source in info.today_news:
        text += '\n \\- %s' % escaped(source)
        for news in info.today_news[source]:
            text += '\n[%s](%s)' % (escaped(news['title']), news['url'])
    info.today_news = {}
    info.sended_news = {}
    context.bot.send_message(
        chat_id=group, text=text, parse_mode='MarkdownV2', disable_web_page_preview=True)
