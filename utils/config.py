import configparser

config_file = 'config.ini'
# config_file = 'config-dev.ini'

config = configparser.RawConfigParser()
config.read(config_file)
owner = config['BOT'].getint('owner')
group = config['BOT'].getint('group')
channel = config['BOT'].getint('channel')
pipe = config['BOT'].getint('pipe')
heartbeatURL = config['BOT']['heartbeat']
webhook = config._sections['WEBHOOK']


def update_config():
    with open(config_file, 'w') as configFile:
        config.write(configFile)
