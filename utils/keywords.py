import sys

sys.path.append('/'.join(sys.path[0].split('/')[:-1]))
from utils.statistics.tfidf import TFIDF
from page_get.user import get_profile

from db.basic_db import db_session
from db.models import WeiboData, KeyWords, KeywordsWbdata, WeiboComment
from sqlalchemy import or_
from utils.statistics.tools import build_init_xls

tfidf = TFIDF()
tfidf.set_stop_words("stop_word.txt")
keys = ['事件名',
        '微博名称',
        '微博属性',
        '认证信息',
        '粉丝拥有量',
        '微博等级',
        '网址',
        '发布时间',
        '转发数',
        '点赞数',
        '评论数',
        ]

for i in range(1, 30):
    count = 1
    keys.append('词汇{}'.format(i))
    keys.append('词频{}'.format(i))

workbook, ws, key_index = build_init_xls(keys)

line_num = 0
finish_count = 0


def main():
    global workbook
    global ws
    if len(sys.argv) > 1:
        arg = sys.argv[1]
    else:
        arg = '四川 茂县'
    keyword = db_session.query(KeyWords).filter(KeyWords.keyword == arg).first()
    if keyword:
        query = db_session.query(WeiboData).filter(
            or_(WeiboData.repost_num >= 500, WeiboData.comment_num >= 500, WeiboData.praise_num >= 500))
        for wbid in db_session.query(KeywordsWbdata.wb_id).filter(KeywordsWbdata.keyword_id == keyword.id):
            wb = query.filter(WeiboData.weibo_id == wbid[0]).first()
            if wb:
                build_one(keyword, wb, ws)
    workbook.save('result.xls')


def percent(a, b):
    return int(a / b * 10000) / 100 if b else 0


def build_one(keyword, wb, ws):
    user = get_profile(wb.uid)

    global line_num
    line_num += 1
    print('{}行开始统计'.format(line_num))
    ws.write(line_num, key_index['事件名'], keyword.keyword)
    ws.write(line_num, key_index['微博名称'], user.name)
    ws.write(line_num, key_index['粉丝拥有量'], user.fans_num)
    ws.write(line_num, key_index['网址'], wb.weibo_url)
    ws.write(line_num, key_index['发布时间'], wb.create_time)
    ws.write(line_num, key_index['微博属性'], user.verify_type)
    ws.write(line_num, key_index['微博等级'], user.level)
    ws.write(line_num, key_index['认证信息'], user.verify_info)
    ws.write(line_num, key_index['点赞数'], wb.praise_num)
    ws.write(line_num, key_index['评论数'], wb.comment_num)

    # 转转发统计
    ws.write(line_num, key_index['转发数'], wb.repost_num)
    i = 1

    sections = ' '.join(map(lambda x: ':'.join(x[0].split('：')[1:]), db_session.query(WeiboComment.comment_cont).filter(
        WeiboComment.weibo_id == wb.weibo_id).all()))

    keywords = tfidf.extract_tags(sections, topK=None, withWeight=True)

    for key in keywords:
        ws.write(line_num, key_index['词汇{}'.format(i)], key[0])
        ws.write(line_num, key_index['词频{}'.format(i)], int(key[1]))
        i += 1
        if i >= 30:
            break

    global finish_count
    finish_count += 1
    print('{}行完成'.format(finish_count))


if __name__ == '__main__':
    main()




    # 事件名为keyword，
