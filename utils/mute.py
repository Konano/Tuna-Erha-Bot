import json
from utils.log import logger
from utils.config import config

with open('data/mute.json', 'r') as file:
    muted = json.load(file)


def mute(update, context):

    logger.info('\\mute ' + json.dumps(context.args))

    if context.args == []:
        context.bot.send_message(
            update.message.chat_id, 'Usage: /mute [source]')
        return

    global muted
    for each in context.args:
        if each not in muted:
            muted.append(each)

    with open('data/mute.json', 'w') as file:
        json.dump(muted, file)

    context.bot.send_message(update.message.chat_id,
                             'Muted: ' + ' '.join(context.args))


def unmute(update, context):

    logger.info('\\unmute ' + json.dumps(context.args))

    if context.args == []:
        context.bot.send_message(
            update.message.chat_id, 'Usage: /unmute [source]')
        return

    global muted
    for each in context.args:
        muted.remove(each)

    with open('data/mute.json', 'w') as file:
        json.dump(muted, file)

    context.bot.send_message(update.message.chat_id,
                             'Unmuted: ' + ' '.join(context.args))


def mute_show(update, context):

    logger.info('\\mute_list')

    text = 'Muted list:'
    for each in muted:
        text += '\n' + each

    context.bot.send_message(update.message.chat_id, text)
