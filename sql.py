import sqlite3
from datetime import datetime, timedelta, time
from sqlite3 import IntegrityError
from data_handle import handle
from loguru import logger


def _exception(fun):
    def inner(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except IntegrityError as e_:
            logger.warning(f'{fun.__name__}: {e_}')
        except Exception as e:
            logger.error(f'{fun.__name__}: {e}')

    return inner


class SQLManager:
    def __init__(self):
        try:
            self.db = sqlite3.connect('source/data.db', check_same_thread=False)
            self.cursor = self.db.cursor()
            self._table_check()
        except Exception as e:
            logger.error(f'DB initialization failed: {e}')
            exit()

    @_exception
    def _exec(self, *args, **kwargs):
        return self.cursor.execute(*args, **kwargs).fetchone()

    @_exception
    def _exec_all(self, *args, **kwargs):
        return self.cursor.execute(*args, **kwargs).fetchall()

    def _table_check(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table' "
        if not self._exec_all(sql):
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
        if not self._exec(sql_exist, (c_name,)):
            self._exec(sql_cou, (c_name, teacher, site))
        self.db.commit()

    def next_lesson(self, delta: int = 0):
        sql = 'select * from sel where time_start > ? order by time_start;'
        datetime_now = datetime.now() + timedelta(minutes=delta)
        if res := self._exec(sql, (datetime_now,)):
            time_start, course_range, c_name, teacher, site = res
        else:
            logger.warning('No Next Lesson')
            return None

        datetime_start = datetime.strptime(time_start, '%Y-%m-%d %H:%M:%S')
        interval = (datetime_start - datetime_now).total_seconds()

        logger.success(f'Get lesson data: {c_name}, {teacher}, {course_range}, {site}.')
        return interval, c_name, teacher, course_range, site

    def lessosns_a_day(self, week):
        sql = 'select course_range, c_name, teacher, site from sel where time_start between ? and ?'
        date_today = datetime.combine(datetime.now().date(), time())
        week_today = date_today.weekday()
        date_s = date_today + timedelta(days=week - week_today)
        date_e = date_s + timedelta(days=1)
        return self._exec_all(sql, (date_s, date_e))
