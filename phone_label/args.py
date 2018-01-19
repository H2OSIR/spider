# -*- coding:utf-8 -*-
"""
    从数据库提取参数
    整合参数，使之符合http_requests的使用
    Example：
        args = {'customer_id':'13131-123151',
                'phone': 95599,
                # 'proxies': {'http': 'http://192.168.0.1:8888',
                #             'https': 'https://192.168.0.1:8888'}
        }
"""

import requests
import pandas as pd
from database import Connect

def extract(sql):
    """"""
    proxy_list = extract_IP()
    # proxy_list = []
    df = extract_args(sql=sql)
    if proxy_list:
        df['proxy'] = pd.Series(
            proxy_list * (int(df.shape[0] / len(proxy_list)) + 1))
    args_list = []
    for each in df.values:
        dic = {}
        dic['customer_id'] = each[0]
        dic['phone'] = each[1]
        if len(each) == 3:
            dic['proxies'] = each[2]
        args_list.append(dic)
    return args_list

def extract_IP():
    """extract IP
    :return  [{'http':'http://192.168.0.1', 'https':'https://192.168.0.1'},
              {'http':'http://192.168.0.1', 'https':'https://192.168.0.1'},
              {'http':'http://192.168.0.1', 'https':'https://192.168.0.1'}
              {'http':'http://192.168.0.1', 'https':'https://192.168.0.1'}
              {'http':'http://192.168.0.1', 'https':'https://192.168.0.1'}]
    """

    url = 'http://s.zdaye.com/?api=201702210856303243&count=10&px=1'
    res = requests.get(url)
    text = res.text
    if 'http://' not in text:
        raise Exception('代理IP获取失败，任务终止。')
    http = text.split(r',')
    proxies = []
    for each in http:
        proxy = {}
        proxy['http'] = each
        proxy['https'] = each.replace('http', 'https')
        proxies.append(proxy)
    return proxies

def extract_args(sql):
    """extract args from database by sql"""
    db = Connect('oracle')
    data = db.read_sql(sql=sql)
    db.engine.close()
    return data


