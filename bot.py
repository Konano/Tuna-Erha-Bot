from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from datetime import datetime, time, timedelta
from pytz import timezone

from utils.config import config, owner, group, pipe, webhook
from utils.log import logger
from utils.mute import mute, unmute, mute_show
from utils.caiyun import caiyun
from utils.pool import auto_delete
from commands.daily import daily_report, weather_report
from commands.washer import washer
from commands.info import info
from commands.gadget import echo, roll, callpolice, new_message, error_callback, register, hitreds, hitreds_init
from commands.weather import forecast, forecast_hourly, weather
from commands.heartbeat import sendHeartbeat

def help(update, context):
    logger.info('\\help')
    text = '''
/weather - 显示当前位置的天气（彩云）
/forecast - 降雨分钟级预报
/forecast_hourly - 天气小时级预报
/mute - 屏蔽发布源
/unmute - 解除屏蔽发布源
/mute_list - 列出所有被屏蔽的发布源
/roll - 从 1 开始的随机数
/callpolice - 在线报警
/washer - 洗衣机在线状态
/register - 一键注册防止失学
/hitreds - 一键打红人
/help - 可用指令说明
'''
    context.bot.send_message(update.message.chat_id, text)


def main():

    updater = Updater(config['BOT']['accesstoken'], use_context=True)
    dp = updater.dispatcher
    jq = updater.job_queue

    dp.add_error_handler(error_callback)

    f_owner = Filters.chat(owner)
    f_group = Filters.chat(group)
    f_pipe = Filters.chat(pipe)

    dp.add_handler(CommandHandler('mute', mute, pass_args=True, filters=(f_owner | f_group)))
    dp.add_handler(CommandHandler('unmute', unmute,pass_args=True, filters=(f_owner | f_group)))
    dp.add_handler(CommandHandler('mute_list', mute_show, filters=(f_owner | f_group)))
    dp.add_handler(CommandHandler('forecast', forecast))
    dp.add_handler(CommandHandler('forecast_hourly', forecast_hourly))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler('roll', roll, pass_args=True))
    dp.add_handler(CommandHandler('washer', washer, pass_args=True))
    dp.add_handler(CommandHandler('callpolice', callpolice))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('echo', echo, filters=f_owner))
    dp.add_handler(CommandHandler('register', register, pass_args=True))
    dp.add_handler(CommandHandler('hitreds', hitreds))
    dp.add_handler(MessageHandler(f_group & Filters.text, new_message))
    dp.add_handler(MessageHandler(f_pipe & Filters.update.channel_post, info))

    jq.run_repeating(caiyun, interval=60, first=0)
    jq.run_repeating(sendHeartbeat, interval=60, first=0)
    jq.run_repeating(auto_delete, interval=60, first=30)
    jq.run_daily(weather_report, time=time(hour=6, tzinfo=timezone('Asia/Shanghai')), context='day')
    jq.run_daily(weather_report, time=time(hour=18, tzinfo=timezone('Asia/Shanghai')), context='night')
    jq.run_daily(daily_report, time=time(hour=23, tzinfo=timezone('Asia/Shanghai')))
    jq.run_daily(hitreds_init, time=time(hour=0, tzinfo=timezone('Asia/Shanghai')))

    # jq.run_daily(daily_report, time=(datetime.now()+timedelta(hours=-8, seconds=10)).time())

    updater.start_webhook(listen=webhook['listen'], port=webhook['port'], url_path=webhook['token'], cert=webhook['cert'], webhook_url=f'https://{webhook["url"]}:8443/{webhook["port"]}/{webhook["token"]}')
    logger.info('bot start')
    updater.idle()


if __name__ == '__main__':
    main()
