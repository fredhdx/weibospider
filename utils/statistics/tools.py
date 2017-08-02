import sys

from sqlalchemy import desc
sys.path.append('/'.join(sys.path[0].split('/')[:-2]))
from utils.time_parser import time_diff
import xlrd
from utils.statistics import tfidf

from db.models import WeiboComment, WeiboRepost, User
import xlwt
from page_get import user
from db.basic_db import db_session
from page_get.user import get_profile


def get_id_from_zw():
    """根据zw.xls文件，返回一组用户uid"""
    wb = xlrd.open_workbook("zw.xls")
    sh = wb.sheet_by_index(0)
    for i in range(1, sh.nrows):
        uid = user.get_uid_by_name(sh.cell(i, 1).value)
        yield uid


def build_init_xls(keywords):
    """根据列名初始化excel,返回excel文件并返回列名字典"""
    wb = xlwt.Workbook()
    ws = wb.add_sheet("data")
    key_index = dict(zip(keywords, range(len(keywords))))
    for k, v in key_index.items():
        ws.write(0, v, k)
    return wb, ws, key_index


def write_xls(ws, line_number, key_index, keyword, value):
    if keyword in key_index:
        ws.write(line_number, key_index[keyword], value)


def write_one_line_data(ws, key_index, line_num, wb):
    """在excel的一行中写上一个微博的统计数据"""
    user = get_profile(wb.uid)

    print('{}行开始统计'.format(line_num))
    write_xls(ws, line_num, key_index, '微博名称', user.name)
    write_xls(ws, line_num, key_index, '粉丝拥有量', user.fans_num)
    write_xls(ws, line_num, key_index, '网址', wb.weibo_url)
    write_xls(ws, line_num, key_index, '发布时间', wb.create_time)
    write_xls(ws, line_num, key_index, '微博属性', user.verify_type)
    write_xls(ws, line_num, key_index, '微博等级', user.level)
    write_xls(ws, line_num, key_index, '认证信息', user.verify_info)
    write_xls(ws, line_num, key_index, '点赞数', wb.praise_num)
    write_xls(ws, line_num, key_index, '评论数', wb.comment_num)
    write_xls(ws, line_num, key_index, '内容', wb.weibo_cont)
    write_xls(ws, line_num, key_index, '转发数', wb.repost_num)

    if "第一层转发" in key_index:
        all_repost = db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wb.weibo_id).count()
        lv1 = db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wb.weibo_id).filter(
            WeiboRepost.lv == 0).count()
        write_xls(ws, line_num, key_index, '第一层转发', percent(lv1, all_repost))
        if "第二层转发" in key_index:
            lv2 = db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wb.weibo_id).filter(
                WeiboRepost.lv == 1).count()
            write_xls(ws, line_num, key_index, '第二层转发', percent(lv2, all_repost))
            if "第三层转发" in key_index:
                lv3 = db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wb.weibo_id).filter(
                    WeiboRepost.lv == 2).count()
                write_xls(ws, line_num, key_index, '第三层转发', percent(lv3, all_repost))
                if "第四层转发" in key_index:
                    lv4 = db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wb.weibo_id).filter(
                        WeiboRepost.lv == 3).count()
                    write_xls(ws, line_num, key_index, '第四层转发', percent(lv4, all_repost))
                    if "四层以上转发" in key_index:
                        lv5 = all_repost - lv1-lv2-lv3-lv4
                        write_xls(ws, line_num, key_index, '四层以上转发', percent(lv5, all_repost))

    ws.write(line_num, key_index['普通用户数量'],
             get_repost_user_count(wb.weibo_id, 0) / all_repost * 100 if all_repost > 0 else 0)
    ws.write(line_num, key_index['个人认证占比'],
             get_repost_user_count(wb.weibo_id, 1) / all_repost * 100 if all_repost > 0 else 0)
    ws.write(line_num, key_index['机构认证占比'],
             get_repost_user_count(wb.weibo_id, 2) / all_repost * 100 if all_repost > 0 else 0)
    if "昵称1" in key_index:
        i = 1
        for keyrepost in db_session.query(WeiboRepost).filter(
                        WeiboRepost.root_weibo_id == wb.weibo_id).order_by(
            desc(WeiboRepost.repost_count))[:10]:
            repost_user = get_profile(keyrepost.user_id)

            write_xls(ws, line_num, key_index, '昵称{}'.format(i), repost_user.name)
            write_xls(ws, line_num, key_index, '粉丝数{}'.format(i), repost_user.fans_num)
            if repost_user.uid == wb.uid:
                write_xls(ws, line_num, key_index, '认证类型{}'.format(i), 11)
            else:
                write_xls(ws, line_num, key_index, '认证类型{}'.format(i), repost_user.verify_type)
            write_xls(ws, line_num, key_index, '微博数{}'.format(i), repost_user.wb_num)
            write_xls(ws, line_num, key_index, '等级{}'.format(i), repost_user.level)
            write_xls(ws, line_num, key_index, '认证信息{}'.format(i), repost_user.verify_info)
            write_xls(ws, line_num, key_index, '转发数{}'.format(i), keyrepost.repost_count)
            write_xls(ws, line_num, key_index, '转发时间{}'.format(i), time_diff(keyrepost.repost_time, wb.create_time))
            i += 1
    if "c昵称1" in key_index:
        i = 1
        for keycomment in db_session.query(WeiboComment).filter(
                        WeiboComment.weibo_id == wb.weibo_id).order_by(
            desc(WeiboComment.like))[:10]:
            comment_user = get_profile(keycomment.user_id)
            write_xls(ws, line_num, key_index, 'c昵称{}'.format(i), comment_user.name)
            write_xls(ws, line_num, key_index, 'c粉丝数{}'.format(i), comment_user.fans_num)
            if comment_user.uid == wb.uid:
                write_xls(ws, line_num, key_index, 'c认证类型{}'.format(i), 11)
            else:
                write_xls(ws, line_num, key_index, 'c认证类型{}'.format(i), comment_user.verify_type)
            write_xls(ws, line_num, key_index, 'c微博数{}'.format(i), comment_user.wb_num)
            write_xls(ws, line_num, key_index, 'c等级{}'.format(i), comment_user.level)
            write_xls(ws, line_num, key_index, 'c认证信息{}'.format(i), comment_user.verify_info)
            write_xls(ws, line_num, key_index, 'c评论时间{}'.format(i), time_diff(keycomment.create_time, wb.create_time))

            # ws.write(line_num, keyindex['次级评论数{}'.format(i)], keycomment.sub_comment_count)
            write_xls(ws, line_num, key_index, 'c点赞数{}'.format(i), keycomment.like)
            i += 1

    print('{}行完成'.format(line_num))


def get_repost_user_count(wbid, verify_type):
    return db_session.query(WeiboRepost).join(User, User.uid == WeiboRepost.user_id).filter(
        WeiboRepost.root_weibo_id == wbid).filter(
        User.verify_type == verify_type).count()


def get_repost_lv_count(wbid, lv):
    db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wbid).filter(
        WeiboRepost.lv == lv).count()


def get_repost_count_by_user(wbid, user_id):
    db_session.query(WeiboRepost).filter(WeiboRepost.root_weibo_id == wbid).filter(
        WeiboRepost.user_id == user_id).order_by(desc(WeiboRepost.repost_count))


def percent(a, b):
    return int(a / b * 10000) / 100 if b else 0

