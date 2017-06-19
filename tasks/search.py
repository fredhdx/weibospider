# coding:utf-8
from datetime import datetime, timedelta
from urllib import parse as url_parse
import time
from db.models import KeyWords, WeiboData, KeywordsWbdata
from logger.log import crawler
from tasks.workers import app
from page_get.basic import get_page
from config.conf import get_max_search_page
from page_parse import search as parse_search
from db.search_words import get_search_keywords
from db.keywords_wbdata import insert_keyword_wbid
from db.wb_data import insert_weibo_data, get_wb_by_mid
from db.basic_db import db_session

# 只抓取原创微博，默认是按照时间进行排序，如果只抓首页，那么就不需要登录
url = 'http://s.weibo.com/weibo/{}&typeall=1&suball=1&page={}&scope=ori'
time_param = '&timescope=custom:{}'
limit = get_max_search_page() + 1


def build_time_param(endtime):
    endtime = endtime.split(':')[0].replace(' ', '-')
    endtime = datetime.strptime(endtime, '%Y-%m-%d-%H')
    endtime -= timedelta(hours=1)
    endtime = endtime.strftime('%Y-%m-%d-%H')
    return endtime


@app.task(ignore_result=True)
def search_keyword(keyword, keyword_id):
    cur_page = 1
    encode_keyword = url_parse.quote(keyword)

    db_keyword = db_session.query(KeyWords).filter(KeyWords.id == keyword_id).first()
    tp = None
    if db_keyword:
        if db_keyword.start_time:
            tt = db_keyword.start_time
            if db_keyword.end_time:
                if db_keyword.end_time == 'auto':
                    end_time = db_session.query(WeiboData).filter(KeywordsWbdata.keyword_id == keyword_id).filter(
                        KeywordsWbdata.wb_id == WeiboData.weibo_id).order_by(WeiboData.create_time).first()
                    if end_time:
                        end_time = end_time.create_time
                        end_time = build_time_param(end_time)
                        tt += ':' + end_time
                else:
                    tt += ':' + db_keyword.end_time
            tp = time_param.format(tt)
    while cur_page < limit:
        cur_url = url.format(encode_keyword, cur_page)
        if tp:
            cur_url += tp
        search_page = get_page(cur_url)
        time.sleep(15)
        if not search_page:
            crawler.warning('本次并没获取到关键词{}的相关微博,该页面源码是{}'.format(keyword, search_page))
            return

        search_list = parse_search.get_search_info(search_page)
        # 先判断数据库里是否存在相关的微博，如果是已有的，那就说明是已经抓取的微博(因为结果默认按时间排序)，就退出循环
        for wb_data in search_list:
            rs = get_wb_by_mid(wb_data.weibo_id)
            if rs:
                crawler.info('关键词{}本次搜索更新的微博已经获取完成'.format(keyword))
                return
            insert_keyword_wbid(keyword_id, wb_data.weibo_id)
            insert_weibo_data(wb_data)
            # 这里暂时使用网络调用而非本地调用，权衡两种方法的好处
            app.send_task('tasks.user.crawl_person_infos', args=(wb_data.uid,), queue='user_crawler',
                          routing_key='for_user_info')

        # 判断是否包含下一页
        if 'page next S_txt1 S_line1' in search_page:
            cur_page += 1
        else:
            crawler.info('关键词{}搜索完成'.format(keyword))
            return


@app.task(ignore_result=True)
def excute_search_task():
    keywords = get_search_keywords()
    for each in keywords:
        app.send_task('tasks.search.search_keyword', args=(each[0], each[1]), queue='search_crawler',
                      routing_key='for_search_info')
