from time import strftime, gmtime
from schedule import Schedule
import json
from threading import Timer as Timer_
from config import c
from loguru import logger

sc = Schedule()
# sc.sc_week().save('1.png')


def recv_handle(content):
    def get_msg(key):
        return content[key] if key in content else ''

    if get_msg('meta_event_type') == 'heartbeat':
        return
    logger.info(f'Get message: {str(content)}')
    # print(content)

    if get_msg('message_type') == 'group':
        data = {'group_id': content['group_id']}
    elif 'user_id' in content:
        data = {'user_id': content['user_id']}
    else:
        return

    if get_msg('message') == '课程表':
        if img := sc.sc_week():
            img.save("{}/source/pictures/schedule_week.png".format(c.path))
            data['message'] = "[CQ:image,file=file:///{}/source/pictures/schedule_week.png]".format(c.path[1:])

    if 'message' in data:
        target = {"action": 'send_msg', 'params': data}
        post_data = json.dumps(target)
        return post_data
    return


def thread_schedule_next(ws):
    def schedule_send():
        try:
            sc.sc_next().save("{}/source/pictures/schedule_next.png".format(c.path))
        except Exception as e:
            logger.error(e)
            exit()

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
        if data := sc.next_time():
            Timer(data, schedule_send)
            f_time = strftime('%dd %Hh %Mm %Ss', gmtime(data))
            logger.info(f'Data will be sent after {f_time}')

    def Timer(*args, **kwargs):
        _ = Timer_(*args, **kwargs)
        _.daemon = True
        _.start()

    timer_set()
