# -*- coding:utf-8 -*-
"""http requests, return html

@author: 4802
"""

import random
import requests
import logging
import traceback
from threading import Thread
from multiprocessing import Pool
from requests.exceptions import ProxyError

User_Agent_List = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]

random_userAgent = User_Agent_List[random.randrange(0, len(User_Agent_List))]

FIRST_URL = {'baidu': 'https://www.baidu.com',
             'haosou': 'https://www.so.com'}

HEADERS = {
    'baidu': {
        'Host': 'www.baidu.com',
        'Referer': 'https://www.baidu.com/',
        'User-Agent': random_userAgent
    },
    'haosou': {
        'Host': 'www.so.com',
        'Referer': 'https://www.so.com/',
        'User-Agent': random_userAgent
    }
}

logger = logging.getLogger('timming_tasks.run.http_requests')

def get_cookies(engine, proxies=None):
    """返回搜索引擎的首页cookies，

    :param engine: the key of first_url，'baidu' or 'haosou'
    :return:
    """

    response = requests.get(url=FIRST_URL[engine],
                            headers=HEADERS[engine],
                            proxies=proxies, timeout=20)

    return response.cookies

def get_html(phone, engine='baidu', proxies=None):
    """return a web page_source code

    :param engine: 'baidu' or 'haosou'
    :param phone: str
    :return: html type is unicode str
    """

    if engine == 'baidu':
        req_url = 'https://www.baidu.com/s'
        params = {'wd': phone}
    else:
        req_url = 'https://www.so.com/s'
        params = {
            'ie': 'utf-8',
            'fr': 'none',
            'src': '360sou_newhome',
            'q': phone
        }
    cookies = get_cookies(engine=engine)
    html = ''
    status = 0
    loop = True
    while loop:
        try:
            response = requests.get(url=req_url, params=params, cookies=cookies,
                                    headers=HEADERS[engine], proxies=proxies,
                                    timeout=20)
            html = response.content
            status = 1
            loop = False
        except Exception as e:
            if isinstance(e, ProxyError):
                proxies = False
            else:
                logger.warning('request failed: phone=%s, engine=%s' % (phone, engine))
                logger.error(traceback.format_exc())
                html = ''
                status = 0
                loop = False
    return {'engine': engine, 'html': html, 'status': status}

class MyThread(Thread):
    """multi-Thread with return values"""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, *, daemon=None):
        Thread.__init__(self, group=group, target=target, name=name,
                        args=args, kwargs=kwargs, daemon=daemon)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def joined(self):
        Thread.join(self)
        return self._return

def search(args):
    """"""

    phone = args.get('phone')
    proxies = args.get('proxies')
    # 将百度和好搜用两个线程一起跑
    t1 = MyThread(target=get_html, args=(phone, 'baidu', proxies))
    t2 = MyThread(target=get_html, args=(phone, 'haosou', proxies))
    threads = [t1, t2]
    for t in threads:
        t.setDaemon(True)
        t.start()
    htmls = []
    for t in threads:
        html = t.joined()
        if html:
            html['phone'] = phone
            html['customer_id'] = args['customer_id']
            htmls.append(html)

    return htmls

def multi_search(args_list, processes=1):
    """"""

    pool = Pool(processes)
    result_list = pool.map(search, args_list)
    all_data = []
    for d in result_list:
        for each in d:  # 每个d包含百度和好搜
            if each:  # 去掉请求失败的，把请求成功的依然返回
                all_data.append(each)
    pool.close()
    pool.join()
    return all_data

if __name__ == '__main__':
    # proxies = {'http':'http://192.168.0.1',
    #            'https':'https://192.168.0.1'}
    args = {'customer_id':'13131-123151', 'phone': 95599}

    search(args=args)
