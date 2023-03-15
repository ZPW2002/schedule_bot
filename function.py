from schedule import Schedule
import json
from threading import Timer as Timer_
from config import c
from loguru import logger

sc = Schedule()


class Data_handle:
    def __init__(self, recv_data):
        self._recv_data = recv_data
        self._data = dict()
        self._target = {"action": 'send_msg', 'params': self._data}
        self._message_type = self._recv_data.get('message_type')
        self.msg_get = self._recv_data.get('message')

        if self._message_type == 'private':
            self._data['user_id'] = self._recv_data.get('user_id')
        elif self._message_type == 'group':
            self._data['group_id'] = self._recv_data.get('group_id')
        # logger.info(f'{str(self._recv_data)}')

    def data_post(self):
        return None if self.fliter_() else json.dumps(self._target)

    def fliter_(self):
        if any([
            self._recv_data.get('meta_event_type') == 'heartbeat',
            (self._message_type != 'private' and self._message_type != 'group'),
            not self._data.get('message')
        ]):
            return True

    def msg_set(self, data):
        self._data['message'] = data


def recv_handle(data_get):
    tar = Data_handle(data_get)

    if tar.msg_get == '课程表':
        sc.sc_week().save("./source/pictures/schedule_week.png")
        tar.msg_set("[CQ:image,file=file:///{}/source/pictures/schedule_week.png]".format(c.path[1:]))

    return tar.data_post()


def thread_schedule_next(ws):
    def schedule_send():
        def data_post(tar):
            total = {"action": 'send_msg'}
            data = {'message': "[CQ:image,file=file:///{}/source/pictures/schedule_next.png]".format(c.path[1:])}
            data.update(tar)
            total['params'] = data
            return json.dumps(total)

        for item in c.send_target:
            ws.send(data_post(item))

        Timer(5, timer_set)

    def timer_set():
        def time_format(raw_time):
            t = int(raw_time)
            days = t // 86400
            hours = (t - days * 86400) // 3600
            minutes = (t - days * 86400 - hours * 3600) // 60
            seconds = t % 60
            return f'{days}d {hours}h {minutes}m {seconds}s'

        if data := sc.sc_next():
            data[0].save("{}/source/pictures/schedule_next.png".format(c.path))
            Timer(data[1], schedule_send)
            # f_time = strftime('%dd %Hh %Mm %Ss', gmtime(data[1]))
            logger.info(f'Data will be sent after {time_format(data[1])}')

    def Timer(*args, **kwargs):
        _ = Timer_(*args, **kwargs)
        _.daemon = True
        _.start()

    timer_set()
