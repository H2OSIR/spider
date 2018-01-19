# -*- coding:utf-8 -*-
"""
    1、读取参数
    2、整合参数
    3、传递参数，网络请求。
    4、提取结构化数据
    5、数据入库

"""
import os
import time
from args import extract
from database import Connect, OUTPUT_TABLE
from http_requests import multi_search
from parse_html import multi_parse
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'   # 防止插入数据时变问号


def sql(start_key, end_key):
    """双开区间"""
    sql = ('SELECT customer_id, fix_phone FROM guhua_1 where key>%s and '
           'key<%s' % (str(start_key), str(end_key + 1)))
    return sql

def start(**kwargs):
    """"""
    t = time.time()
    sql = kwargs.get('sql')
    if not sql:
        raise Exception('必须传入一个sql参数')
    args = extract(sql=sql)     # 提取参数
    # args = [{'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599},
    #         {'customer_id': '13131-123151', 'phone': 95599}]
    print('-----start searching-----')
    html_list = multi_search(args_list=args, processes=2)  # 查询参数
    print('-----start parsing-----')
    result = multi_parse(html_list, processes=4)     # 多线程解析html
    db = Connect('ORACLE')
    # result = [{
    #     # 'ID': 100001,
    #     'CUSTOMER_ID': 'aa',
    #     'PHONE': 'aa',
    #     'ADDRESS': 'aa',
    #     'ENGINE': 'aa',
    #     'LABEL_USER': 'aa',
    #     'LABEL_NUMBER': 'aa',
    #     'LABEL_TYPE': 'aa',
    #     'LABEL': 'aa',
    #     'TIP': 'aa',
    #     'SOURCE_URL': 'aa',
    #     'ABSTRACT': 'aa',
    #     'CREATE_TIME': '',
    #     'STATUS': 0},
    #         {
    #             # 'ID': 100002,
    #             'CUSTOMER_ID': 'aa',
    #             'PHONE': 'aa',
    #             'ADDRESS': 'aa',
    #             'ENGINE': 'aa',
    #             'LABEL_USER': 'aa',
    #             'LABEL_NUMBER': 'aa',
    #             'LABEL_TYPE': 'aa',
    #             'LABEL': 'aa',
    #             'TIP': 'aa',
    #             'SOURCE_URL': 'aa',
    #             'ABSTRACT': 'aa',
    #             'CREATE_TIME': '',
    #             'STATUS': 0}
    #     ]
    result = db.add_index(result)
    print('-----writing to database-----')
    db.write_sql(result, OUTPUT_TABLE)  # 插入数据库
    print('Finished:', time.time() - t)

if __name__ == '__main__':
    sql = sql(3400, 3450)
    start(sql=sql)
