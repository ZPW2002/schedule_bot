from time import strftime, gmtime

from PIL import Image, ImageDraw, ImageFont
import random
import json
from threading import Timer as Timer_
from sql import SQLManager
from config import c
from loguru import logger


def Timer(*args, **kwargs):
    _ = Timer_(*args, **kwargs)
    _.daemon = True
    _.start()


def schedule_picture(data):
    c_name, teacher, c_range, site = data
    color = random.randint(0, 11)
    img = Image.open('{}/source/pictures/t{}.png'.format(c.path, color))
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(c.font_path, 60)
    tit_len = len(c_name)
    text = c_name if tit_len <= 11 else c_name[:11] + '...'
    x_px = 410 - 30 * min(tit_len, 11)
    draw.text((x_px, 40), text, 'black', font)

    time_text = c.time_range(c_range)

    font = ImageFont.truetype(c.font_path, 40)
    draw.text((150, 238), teacher, 'grey', font)
    draw.text((150, 338), time_text, 'grey', font)
    draw.text((150, 438), site, 'grey', font)
    return img


def thread_schedule_next(ws):
    db = SQLManager()

    def schedule_send(sc_data):
        try:
            schedule_picture(sc_data).save("{}/source/pictures/schedule_next.png".format(c.path))
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

        timer_set()

    def timer_set():
        if data := db.next_lesson():
            interval = data[0] - c.send_before*60
            Timer(interval, schedule_send, (data[1:], ))
            f_time = strftime('%Hh %Mm %Ss', gmtime(interval))
            logger.info(f'Data will be sent after {f_time}')

    timer_set()
