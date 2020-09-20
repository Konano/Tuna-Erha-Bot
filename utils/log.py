import logging
from utils.config import config

BASIC_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(funcName)s - %(message)s'
DATE_FORMAT = None
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)

chlr = logging.StreamHandler()
chlr.setFormatter(formatter)
chlr.setLevel('INFO')

fhlr = logging.handlers.TimedRotatingFileHandler(
    config['BOT']['logpath'] + 'server', when='D', interval=1, backupCount=30)
fhlr.setFormatter(formatter)
fhlr.setLevel('DEBUG')

logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')
logger.addHandler(chlr)
logger.addHandler(fhlr)
