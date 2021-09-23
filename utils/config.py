import configparser

config = configparser.RawConfigParser()
config.read('config.ini')
owner = config['BOT'].getint('owner')
group = config['BOT'].getint('group')
channel = config['BOT'].getint('channel')
pipe = config['BOT'].getint('pipe')
heartbeatURL = config['BOT']['heartbeat']
webhook = config._sections['WEBHOOK']


def update_config():
    with open('config.ini', 'w') as configFile:
        config.write(configFile)


connectTimeLimit = 10


class InvalidParameter(Exception):
    """Invalid Parameter"""


class ConnectError(Exception):
    """Connect Error"""


class ConnectTimeout(Exception):
    """Connect Timeout"""
