from telegram.ext import Updater, CommandHandler, Filters, MessageHandler
from utils.config import config, owner, group, pipe
from utils.log import logger
from utils.mute import mute, unmute, mute_show
from utils.caiyun import caiyun
from commands.daily import daily_report
from commands.washer import washer
from commands.info import info
from commands.gadget import echo, roll, callpolice, new_message, error_callback, register, hitreds, hitreds_init
from commands.weather import forecast, forecast_hourly, weather
from commands.heartbeat import sendHeartbeat
import datetime, pytz

def help(update, context):
    logger.info('\\help')
    text = '''
可用：

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
/help - 可用指令说明

废弃：

/libseat - 查看文图座位剩余情况
/weather_thu - 显示学校区域当前的天气（学校天气站）
/weather_today - 显示当前位置的今日天气预报（彩云）
/status - Bot 连接状态
'''
    context.bot.send_message(update.message.chat_id, text)


def main():

    if config['BOT'].getboolean('proxy'):
        updater = Updater(config['BOT']['accesstoken'], use_context=True, request_kwargs={
                          'proxy_url': config['BOT']['socks5']})
    else:
        updater = Updater(config['BOT']['accesstoken'], use_context=True)

    dp = updater.dispatcher

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

    updater.job_queue.run_repeating(caiyun, interval=60, first=0, context=group)
    updater.job_queue.run_repeating(daily_report, interval=10, first=0, context=group)
    updater.job_queue.run_repeating(sendHeartbeat, interval=60, first=0)
    updater.job_queue.run_daily(hitreds_init, time=datetime.time(hour=0, minute=0, tzinfo=pytz.timezone('Asia/Shanghai')))

    dp.add_error_handler(error_callback)

    logger.info('bot start')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
