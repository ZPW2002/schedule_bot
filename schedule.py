from PIL import ImageDraw, Image, ImageFont
from config import c
from sql import SQLManager
import random
from datetime import datetime
from random import sample


def _font(font_size):
    return ImageFont.truetype(c.font_path, font_size)


# 颜色生成器
def _color_gen():
    color_light = [
        "#E5F4FF", "#FDEBDE", "#DEFBF8", "#EDEDFF", "#FCEBCD", "#FFEFF0",
        "#EAF1FF", "#FFEDF8", "#E2F8F3", "#FFF8C8", "#F9EDFF", "#F3F2FD",
    ]
    color_dark = [
        "#00A6F2", "#FC6B50", "#3CB3C8", "#7D7AEA", "#FF9900", "#EF5B75",
        "#5B8EFF", "#F067BB", "#29BBAA", "#CBA713", "#B967E3", "#6E8ADA",
    ]
    temp = sample(list(range(10)), 10)
    while True:
        for t in temp:
            yield color_light[t], color_dark[t]


class Schedule:
    def __init__(self, size=(2200, 1540)):
        # self.x, self.y = (2200, 1540)
        self.x, self.y = size
        self.cell_x = self.x * 3 // 22
        self.cell_y = self.y // (c.class_num + 1)
        self.db = SQLManager()
        self.font_size = self.y * 2 // 77
        self.width = self.font_size // 10

    # 下一节课图片
    def sc_next(self):
        if not (data := self.db.next_lesson(c.send_before)):
            return None

        c_name, teacher, c_range, site = data[1:]
        time_text = c.time_range(c_range)
        color = random.randint(0, 11)
        img = Image.open('{}/source/pictures/t{}.png'.format(c.path, color))
        draw = ImageDraw.Draw(img)

        tit_len = len(c_name)
        text = c_name if tit_len <= 11 else c_name[:11] + '...'
        x_px = 410 - 30 * min(tit_len, 11)
        draw.text((x_px, 40), text, 'black', _font(60))

        draw.text((150, 238), teacher, 'grey', _font(40))
        draw.text((150, 338), time_text, 'grey', _font(40))
        draw.text((150, 438), site, 'grey', _font(40))
        return img

    # 周课程表图片
    def sc_week(self, has_weekend=False):
        bg = self._table_background()
        c_ = _color_gen()

        # 格子坐标
        pos = {
            week_: {
                class_: (
                    self.cell_x // 3 + week_ * self.cell_x + self.width * 3 // 4,
                    self.cell_y * class_ - self.width * 5 // 4
                )
                for class_ in range(1, c.class_num + 1)
            }
            for week_ in range(7)
        }
        for week in range(7):
            for item in self.db.lessosns_a_day(week):
                class_ = int(item[0].split('-')[0]) + 1
                bg.paste(self._lesson_unit(item, c_), pos[week][class_])

        # 最终图片
        tar_x = self.x + 2 * (has_weekend - 1) * self.cell_x
        tar_y = self.y + self.cell_y
        x_pos = tar_x // 2 - 2.5 * self.font_size // 2
        week_num = (datetime.now().date() - c.course_start).days // 7 + 1

        tar = Image.new('RGB', (tar_x, tar_y), 'white')
        tar.paste(bg, (0, self.cell_y))
        draw = ImageDraw.Draw(tar)
        draw.text((x_pos, 10), f'第{week_num}周', 'black', _font(2 * self.font_size))
        return tar

    # 是否存在下一节课
    def next_time(self):
        if res := self.db.next_lesson(c.send_before):
            return res[0]

    # 课程表背景图片
    def _table_background(self):
        img = Image.new('RGB', (self.x, self.y), 'white')
        draw = ImageDraw.Draw(img)

        # 横格子线+其他
        def time_list(cla):
            draw.text(
                xy=(self.font_size, self.cell_y * cla),
                text=f'{cla}',
                fill='black',
                font=_font(self.font_size)
            )
            for _ in range(2):
                draw.text(
                    xy=(self.font_size // 2, (1 + _) * self.font_size + self.cell_y * cla),
                    text=str(c.timetable[cla - 1][_]),
                    fill='grey',
                    font=_font(3 * self.font_size // 4)
                )
            draw.line(
                xy=[(0, self.cell_y * cla - 2 * self.width), (self.x, self.cell_y * cla - 2 * self.width)],
                fill='#f4f4f4',
                width=self.width
            )

        # 竖格子线+其他
        def week_list():
            list_text = [f'周{_}' for _ in ['一', '二', '三', '四', '五', '六', '日']]
            for _, item in enumerate(list_text):
                draw.text(
                    xy=(2 * self.cell_x // 3 + self.cell_x * _, self.cell_y // 2),
                    text=item,
                    fill='black',
                    font=_font(self.font_size)
                )
                draw.line(
                    xy=[
                        (self.cell_x // 3 + self.cell_x * _, self.cell_y - 2 * self.width),
                        (self.cell_x // 3 + self.cell_x * _, self.y)
                    ],
                    fill='#f4f4f4',
                    width=self.width
                )

        for i_ in range(1, c.class_num + 1):
            time_list(i_)
        week_list()
        return img

    # 每一节课的卡片
    def _lesson_unit(self, data, c_):
        c_light, c_dark = next(c_)
        width = self.cell_x
        height = (1 - eval(data[0])) * self.cell_y
        img = Image.new('RGB', (width - self.width, height - self.width), 'white')
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            xy=((self.width, self.width), (width - 2 * self.width - 1, height - 2 * self.width - 1)),
            fill=c_light,
            width=self.width
        )
        word_num = len(data[1])

        name_ = data[1] if word_num <= 20 else f'{data[1][:19]}...'
        y_sub = 30
        if word_num > 6:
            name_ = f'{name_[:6]}\n{name_[6:]}'
            y_sub += 20
        sub_data = f'@{data[3]}\n{data[2]}'
        draw.text((self.font_size // 2, self.cell_y // 7), name_, c_dark, _font(self.font_size))
        draw.text((self.font_size // 2, self.cell_y), sub_data, c_dark, _font(3 * self.font_size // 4))
        return img
