"""根据用户获取统计数据"""
import sys

sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from utils.statistics.const import get_common_keys
from db.models import User, WeiboData
from db.basic_db import db_session
from utils.statistics.tools import build_init_xls, write_one_line_data

keys = get_common_keys()


def main():
    workbook, ws, key_index = build_init_xls(keys)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        arg = '烧伤超人阿宝'
    user = db_session.query(User).filter(User.name == arg).first()
    line_num = 1
    for wbb in db_session.query(WeiboData).filter(WeiboData.uid == user.uid).filter(
                    WeiboData.create_time > "2017-06-24"):
        write_one_line_data(ws, key_index, line_num, wbb)
        line_num += 1
    workbook.save("result.xls")


if __name__ == "__main__":
    main()
