import json
import websocket
from websocket import WebSocketConnectionClosedException
from function import thread_schedule_next, recv_handle
import time
from loguru import logger
from config import c


class Websocket_:
    def __init__(self):
        self._ws = None
        self.host = c.host
        self.connect()

    def connect(self):
        while True:
            try:
                self._ws = websocket.create_connection(self.host)
                logger.success(f'Connect to {self.host}')
                break
            except Exception as e:
                logger.error(f'Websocket error: {e}')
                time.sleep(3)

    def send(self, *args, **kwargs):
        try:
            self._ws.send(*args, **kwargs)
            logger.success('Send: {}'.format(str(*args, **kwargs)))
        except Exception as e:
            logger.error(f'Post error. {e}')

    def recv_(self):
        while True:
            try:
                if post_data := recv_handle(json.loads(self._ws.recv())):
                    self.send(post_data)
            except WebSocketConnectionClosedException as connect_e:
                logger.error(connect_e)
                self.connect()
            except Exception as e:
                logger.error(e)
                exit()


if __name__ == '__main__':
    ws = Websocket_()
    thread_schedule_next(ws)
    ws.recv_()
