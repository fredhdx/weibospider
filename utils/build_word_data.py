import xlrd
import sys
import xlwt

sys.path.append('/'.join(sys.path[0].split('/')[:-1]))

from db.basic_db import db_session
from db.models import WeiboData, KeyWords, KeywordsWbdata, User, WeiboRepost, WeiboComment

wk = xlrd.open_workbook("数据6.xlsx")
sheet = wk.sheet_by_index(0)

goal = xlwt.Workbook()
g_sh = goal.add_sheet("0")
for i in range(1, 3002):
    print(i)
    uid = sheet.cell(i, 1).value
    verify_type = sheet.cell(i, 8).value
    user = db_session.query(User.verify_info).filter(User.uid == uid).first()
    g_sh.write(int(i - 1), 0, verify_type)
    g_sh.write(int(i - 1), 1, user[0])

goal.save("文本数据.xlsx")
