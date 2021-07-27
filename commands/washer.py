import requests
import json

from utils.log import logger
from utils.config import mopenid


def washer_status(obj):
    status_str = obj['washerName'] + '：'
    if obj['runingStatus'] != 48:
        status_str += '运行中...'
        status_str += '剩余' + str(obj['remainRunning']) + '分钟'
    else:
        status_str += '空闲！'
    return status_str


def get_washer(strs):
    cookies = {'mopenid': mopenid}
    try:
        res = requests.get(
            'https://hisun.cleverschool.cn/washWeChat/member/washer/list?regionId=3&pageSize=600&pageNo=1', cookies=cookies, timeout=(5, 10))
    except requests.exceptions.RequestException:
        return '网络错误。'
    ret = json.loads(res.content.decode('utf-8'))['result']
    rpc = [('紫金公寓', '紫荆'), ('紫荊', '紫荆'), ('紫荆公寓', '紫荆'), ('4G', ''), ('三号院', '3号院'), ('七号楼', '7号楼'),
           ('紫荆1号楼1号机', '紫荆1号楼1层1号机'), ('紫荆1号楼4号机', '紫荆1号楼1层4号机'), ('清华大学', ''), ('层3号楼', '层3号机'), ('层4号楼', '层4号机')]
    reply = []
    for i in range(len(ret)):
        for c in rpc:
            ret[i]['washerName'] = ret[i]['washerName'].replace(c[0], c[1])
        if min([ret[i]['washerName'].find(s) for s in strs]) != -1:
            reply.append(washer_status(ret[i]))
    if reply == []:
        return '查询无结果，请检查参数是否正确。'
    elif len(reply) > 20:
        reply.sort()
        return '\n'.join(reply[:20]) + '\n...'
    else:
        reply.sort()
        return '\n'.join(reply)


def washer(update, context):

    logger.info('\\washer {} '.format(
        update.message.chat_id) + json.dumps(context.args))

    if len(context.args) == 0:
        args = ['紫荆2号楼']
    else:
        args = context.args

    context.bot.send_message(update.message.chat_id, get_washer(args))
