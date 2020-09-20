import requests

from utils.log import logger
from utils.config import heartbeatURL


def sendHeartbeat(context):

    logger.debug('heartbeat')
    try:
        requests.get(url=heartbeatURL, timeout=(5, 10))
    except Exception as e:
        logger.error(e)
