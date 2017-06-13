from datetime import datetime

import dateparser


def parse_time_str(s_time):
    create_time = parse_time(s_time)
    if create_time:
        return create_time.strftime("%Y-%m-%d %H:%M")
    else:
        raise Exception('解析错误')


def parse_time(s_time):
    create_time = s_time
    if '月' in create_time and '年' not in create_time:
        create_time = "{}年{}".format(datetime.now().year, create_time)
    if '今天' in create_time:
        create_time = create_time.replace('今天', '')
    create_time = dateparser.parse(create_time)
    return create_time


def time_diff(s_time, e_time):
    last = parse_time(e_time)
    before = parse_time(s_time)
    diff = (last - before).seconds
    diff //= 60
    return str(diff) + '分'
