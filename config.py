from ruamel.yaml import YAML
from datetime import time
import os


class Config:
    def __init__(self):
        with open('config.yaml', 'r', encoding='utf-8') as file:
            config_ = YAML(typ='safe').load(file)
        self.host = config_.get('host')
        self.course_start = config_.get('course_start')
        self.send_target = config_.get('send_target')
        self.send_before = config_.get('send_before')
        self.timetable = config_.get('timetable')

        self.class_num = len(self.timetable)
        self.path = os.getcwd()
        self.font_path = "{}/source/HGY3_CNKI.TTF".format(self.path)
        self.time_start = [time(*map(int, item[0].split(':'))) for item in self.timetable]

    def time_range(self, s):
        s, e = map(int, s.split('-'))
        return '{}-{}'.format(self.timetable[s][0], self.timetable[e][1])


c = Config()
