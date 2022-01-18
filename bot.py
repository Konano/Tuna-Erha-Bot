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
from commands.gadget import yue, gu, fan, san, payme, payme_upload
from commands.weather import forecast, forecast_hourly, weather
from commands.heartbeat import sendHeartbeat


def help(update, context):  # TODO 增加 group 区分
    logger.info('\\help')
    commands = [
        ['weather', '清华目前的天气', True],
        ['forecast', '清华降雨分钟级预报', True],
        ['forecast_hourly', '清华天气小时级预报', True],
        ['mute', '屏蔽发布源', False],
        ['unmute', '解除屏蔽发布源', False],
        ['mute_list', '列出所有被屏蔽的发布源', False],
        ['roll', '从 1 开始的随机数', True],
        ['callpolice', '在线报警', True],
        ['washer', '洗衣机在线状态', True],
        ['register', '一键注册防止失学', True],
        ['hitreds', '一键打红人', True],
        ['spankreds', '给红人来一巴掌', True],
        ['payme', '显示你的收款码', False],
        ['fan', '发起约饭', False],
        ['yue', '约~', False],
        ['buyue', '不约~', False],
        ['san', '饭饱散伙', False],
        ['help', '可用指令说明', True],
    ]
    if update.message.chat_id == group:
        text = '\n'.join([f'/{x[0]} - {x[1]}' for x in commands])
    else:
        text = '\n'.join([f'/{x[0]} - {x[1]}' for x in filter(lambda x:x[-1], commands)])
    context.bot.send_message(update.message.chat_id, text)


def main():

    updater = Updater(config['BOT']['accesstoken'], use_context=True)
    dp = updater.dispatcher
    jq = updater.job_queue

    dp.add_error_handler(error_callback)

    f_owner = Filters.chat(owner)
    f_group = Filters.chat(group)
    f_pipe = Filters.chat(pipe)

    dp.add_handler(CommandHandler('mute', mute, pass_args=True, filters=(f_owner | f_group)))  # TODO 增加 source 和 keyword
    dp.add_handler(CommandHandler('unmute', unmute, pass_args=True, filters=(f_owner | f_group)))  # TODO 增加 source 和 keyword
    dp.add_handler(CommandHandler('mute_list', mute_show, filters=(f_owner | f_group)))  # TODO mute 列表
    dp.add_handler(CommandHandler('forecast', forecast))
    dp.add_handler(CommandHandler('forecast_hourly', forecast_hourly))
    dp.add_handler(CommandHandler('weather', weather))
    dp.add_handler(CommandHandler('roll', roll, pass_args=True))
    dp.add_handler(CommandHandler('washer', washer, pass_args=True))
    dp.add_handler(CommandHandler('callpolice', callpolice))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('echo', echo, filters=f_owner))
    dp.add_handler(CommandHandler('register', register, pass_args=True))
    dp.add_handler(CommandHandler('hitreds', hitreds, filters=(~f_group)))
    dp.add_handler(CommandHandler('spankreds', hitreds, filters=(~f_group)))
    dp.add_handler(CommandHandler('yue', yue, filters=f_group))
    dp.add_handler(CommandHandler('buyue', gu, filters=f_group))
    dp.add_handler(CommandHandler('fan', fan, filters=f_group))
    dp.add_handler(CommandHandler('san', san, filters=f_group))
    dp.add_handler(CommandHandler('payme', payme, filters=f_group))
    dp.add_handler(MessageHandler(Filters.chat() & Filters.photo, payme_upload))
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
