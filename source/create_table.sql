create table course
(
    c_name  text primary key,
    teacher text,
    site text
);
create table schedule
(
    time_start  DATETIME primary key,
    course_range text,
    c_name text,
    foreign key (c_name) references course(c_name)
);
create view sel as
select time_start, course_range, schedule.c_name, teacher, site
from schedule, course
where schedule.c_name=course.c_name;