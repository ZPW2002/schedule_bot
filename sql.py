import sqlite3
from datetime import datetime, timedelta
from sqlite3 import IntegrityError
from data_handle import handle
from loguru import logger


class SQLManager:
    def __init__(self):
        try:
            self.db = sqlite3.connect('source/data.db', check_same_thread=False)
            self.cursor = self.db.cursor()
            self._table_check()
        except Exception as e:
            logger.error(f'DB initialization failed: {e}')
            exit()

    def _exec(self, *args, **kwargs):
        try:
            res = self.cursor.execute(*args, **kwargs).fetchone()
        except IntegrityError:
            logger.warning('Primary Key Conflict, Insert canceled!')
        except Exception as e:
            logger.error(e)
        else:
            return res

    def _table_check(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table' "
        if not self.cursor.execute(sql).fetchall():
            self.cursor.executescript(open('source/create_table.sql').read())
            logger.warning('DataFile not found. Building...')
            if not handle(self):
                self._exec('drop table schedule;')
                self._exec('drop table course;')
                logger.error('Data handing failed. Exit')
                exit()

    def insert(self, time_start, course_range, c_name, teacher, site):
        sql_sc = "insert into schedule values(?,?,?);"
        sql_cou = "insert into course values (?,?,?);"
        sql_exist = 'select * from course where c_name=?;'

        self._exec(sql_sc, (time_start, course_range, c_name))
        if not self._exec(sql_exist, (c_name, )):
            self._exec(sql_cou, (c_name, teacher, site))
        self.db.commit()

        log_info = ', '.join(map(str, [time_start, course_range, c_name, teacher, site]))
        logger.success(f'Insert: {log_info}')

    def next_lesson(self, delta: int = 0):
        sql_sc = 'select * from schedule where time_start > ? order by time_start;'
        sql_cou = 'select teacher, site from course where c_name=?'
        datetime_now = datetime.now() + timedelta(minutes=delta)
        if res := self._exec(sql_sc, (datetime_now, )):
            time_start, course_range, c_name = res
        else:
            logger.warning('No Next Lesson')
            return None
        teacher, site_all = self._exec(sql_cou, (c_name, ))
        site_list = site_all.split(',')
        site = f'{site_list[0]}...' if len(site_list) > 1 else site_list[0]

        datetime_start = datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S')
        interval = (datetime_start - datetime_now).total_seconds()

        logger.success(f'Get lesson data: {c_name}, {teacher}, {course_range}, {site}.')
        return interval, c_name, teacher, course_range, site
