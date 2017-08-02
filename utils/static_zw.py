import sys

import xlwt
sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from utils.statistics.tools import get_id_from_zw, build_init_xls, write_one_line_data
from db.basic_db import db_session
from db.models import WeiboData, User

keywords = ['网址', "发布时间", "转发数", "点赞数", "评论数", "内容"]
wb = xlwt.Workbook()

for id in get_id_from_zw():
    if not id:
        continue
    name = db_session.query(User.name).filter(User.uid == id).first()
    if name:
        name = name[0]
    else:
        continue
    print(name)
    ws = wb.add_sheet(name)
    key_index = dict(zip(keywords, range(len(keywords))))
    for k, v in key_index.items():
        ws.write(0, v, k)
    line_num = 1
    for wbb in db_session.query(WeiboData).filter(WeiboData.uid == id).filter(WeiboData.create_time>"2017"):
        write_one_line_data(ws, key_index, line_num, wbb)
        line_num+=1
wb.save("result.xls")