# import json
# from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SOL_TCP, SO_KEEPALIVE, TCP_KEEPIDLE, TCP_KEEPINTVL, TCP_KEEPCNT, timeout

# from utils.log import logger
# from utils.config import config

# TRANSFER_SUCC = 0
connectStatus = True # FIXME connectStatus should be False

# def connectSocket():

#     mainSocket = socket(AF_INET,SOCK_STREAM)
#     mainSocket.bind((config['SERVER']['ip'], config['SERVER'].getint('port')))
#     mainSocket.listen(1)

#     global serverSocket, connectStatus
#     logging.info('Wait for connection...')
#     connectStatus = False
#     serverSocket,destAdr = mainSocket.accept()
#     serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
#     serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
#     serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
#     serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
#     logging.info('Connect establish!')
#     connectStatus = True

#     global TRANSFER_SUCC, INFO_UPDATE
#     while True:
#         try:
#             try:
#                 serverSocket.settimeout(300)
#                 msg = serverSocket.recv(65536).decode('utf8')
#             except timeout:
#                 serverSocket.send('T'.encode('utf8'))
#                 try:
#                     serverSocket.settimeout(3)
#                     serverSocket.recv(8)
#                 except timeout:
#                     raise
#                 else:
#                     TRANSFER_SUCC += 1
#                     if TRANSFER_SUCC % 10 == 0:
#                         logging.info('TRANSFER_SUCC * 10')
#                     continue

#             logging.info(msg)
#             if msg == '':
#                 raise
#             if msg[0] == 'W':     # weather
#                 global WEATHER_THU_REQUEST, WEATHER_THU_DATA
#                 WEATHER_THU_DATA = json.loads(msg[1:])
#                 WEATHER_THU_REQUEST = False
#                 serverSocket.send('S'.encode('utf8'))
#             # elif msg[0] == 'R':
#             #     logging.info(msg)
#             #     global RAIN_UPDATE
#             #     if msg[1] == 'S':
#             #         RAIN_UPDATE = +1
#             #     elif msg[1] == 'E':
#             #         RAIN_UPDATE = -1
#             #     serverSocket.send('S'.encode('utf8'))
#             elif msg[0] == 'I':
#                 lock.acquire()
#                 try:
#                     global newMessages
#                     newMessages.extend(json.loads(msg[1:]))
#                     INFO_UPDATE = True
#                 except Exception as e:
#                     logging.error(e)
#                 lock.release()
#                 serverSocket.send('S'.encode('utf8'))
#             elif msg[0] == 'D':
#                 lock.acquire()
#                 try:
#                     global delMessages
#                     delMessages.extend(json.loads(msg[1:]))
#                     INFO_UPDATE = True
#                 except Exception as e:
#                     logging.error(e)
#                 lock.release()
#                 serverSocket.send('S'.encode('utf8'))

#         except:
#             logging.exception('Connect Error')
#             serverSocket.close()
#             logging.info('Wait for connection...')
#             serverSocket,destAdr = mainSocket.accept()
#             serverSocket.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
#             serverSocket.setsockopt(SOL_TCP, TCP_KEEPIDLE, 10)
#             serverSocket.setsockopt(SOL_TCP, TCP_KEEPINTVL, 6)
#             serverSocket.setsockopt(SOL_TCP, TCP_KEEPCNT, 20)
#             logging.info('Connect establish!')
#             continue

#     serverSocket.close()
#     mainSocket.close()
