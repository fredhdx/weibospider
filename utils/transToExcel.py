import sys
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from utils.statistics.const import get_common_keys
from db.basic_db import db_session
from db.models import WeiboData, KeyWords, KeywordsWbdata
import xlwt
from sqlalchemy import or_
from utils.statistics.tools import build_init_xls, write_one_line_data

keys = get_common_keys()
line_num = 0
finish_count = 0


def main():
    workbook, ws, key_index = build_init_xls(keys)
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        arg = '四川 茂县'
    keyword = db_session.query(KeyWords).filter(KeyWords.keyword == arg).first()
    line_num = 1
    if keyword:
        query = db_session.query(WeiboData).filter(
            or_(WeiboData.repost_num >= 500, WeiboData.comment_num >= 500, WeiboData.praise_num >= 500))
        for wbid in db_session.query(KeywordsWbdata.wb_id).filter(KeywordsWbdata.keyword_id == keyword.id):
            wb = query.filter(WeiboData.weibo_id == wbid[0]).first()
            if wb:
                write_one_line_data(ws, key_index, line_num, wb)
                line_num += 1
    workbook.save('result.xls')


if __name__ == '__main__':
    main()




    # 事件名为keyword，
