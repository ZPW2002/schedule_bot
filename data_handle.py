from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from config import c
from loguru import logger


def handle(db):
    with open('all.txt', 'rb') as file:
        if content := file.read():
            soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
        else:
            logger.warning("Nothing in 'all.txt'! Fail to create DataFile")
            return False
    data = [
        ';'.join([
            str(item['id']),
            str(item['title']),
            str(item['rowspan'])
        ])
        for item in soup.find_all('td', class_="infoTitle")
    ]

    for item in data:
        temp = [i for i in item.split(';') if i]

        data_class = int(temp[0].split('_')[0].split('D')[1])
        day_of_week, sec = data_class // 10 + 1, data_class % 10
        data_info = temp[2].strip('()').split(',')

        site_list = [item.split('（')[0] for item in data_info[1:]]
        data_info[1] = data_info[1].split('（')[0]
        class_len = int(temp[3])

        # 课程名称
        class_name = temp[1].split(' ')[0].split('(')[0]
        # 教师
        teacher = temp[1].split(' ')[1].strip('()')
        # 第几节开始, 第几节结束
        lesson_start, lesson_end = sec, sec + class_len - 1
        # 教室
        site = ','.join(site_list)

        # 都有哪几周上这节课
        week_list = [
            j for i in data_info[0].split(' ')
            for j in list(
                range(int(i.split('-')[0]), int(i.split('-')[-1]) + 1)
            )
        ]

        for it in week_list:
            delta = timedelta(it * 7 + day_of_week - 8)
            course_date = c.course_start + delta
            course_datetime = datetime.combine(course_date, c.time_start[lesson_start])

            course_range = f'{lesson_start}-{lesson_end}'

            db.insert(course_datetime, course_range, class_name, teacher, site)

    logger.success('Data file created')
    return True
