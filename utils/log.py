import logging, colorlog
from utils.config import config

BASIC_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s'
COLOR_FORMAT = '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s'
DATE_FORMAT = None
basic_formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
color_formatter = colorlog.ColoredFormatter(COLOR_FORMAT, DATE_FORMAT)

chlr = logging.StreamHandler()
chlr.setFormatter(color_formatter)
chlr.setLevel('INFO')

fhlr = logging.handlers.TimedRotatingFileHandler(
    config['BOT']['logpath'] + 'server', when='H', interval=1, backupCount=240)
fhlr.setFormatter(basic_formatter)
fhlr.setLevel('DEBUG')

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(chlr)
logger.addHandler(fhlr)
