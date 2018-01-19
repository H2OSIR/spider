# -*- coding:utf-8 -*-
"""parse html from http_requests

@author: 4802
"""

import re
import pandas as pd
from bs4 import BeautifulSoup
from multiprocessing import Pool

class Phone(object):
    """声明类，定义所需要的一些属性（字段）"""

    def __init__(self):
        self.data = {
            # 结束后需要加个ID，number类型
            'customer_id': '',      # 客户id
            'phone':'',             # 号码
            'address': '',          # 所属地区
            'engine': '',           # 搜索引擎
            'label_user': '',       # 标记用户
            'label_number': '',     # 标记人数
            'label_type': '',       # 标记类型
            'label': '',            # 标记
            'tip': '',              # 友情提示
            'source_url': '',       # 来源网址
            'abstract': '',         # 摘要
            'create_time':'',       # 创建时间
            'status': 0             # 查询状态，1：成功，0：失败
        }

class BaiduHtml(Phone):
    """解析百度的html"""

    def __init__(self, html):
        super(BaiduHtml, self).__init__()    # 继承父类init
        self.html = html
        self.data['engine'] = '百度'

    def get_address(self):
        """获取号码所属地区"""

        soup = BeautifulSoup(self.html, 'lxml')
        address = soup.find(name='span',
                            class_=['op_fraudphone_addr c-gap-right-small'])
        if address:
            address = address.text.replace(' ', '-')
        elif soup.find(name='div',
                       class_=['op_mobilephone_r c-gap-bottom-small']):
            address = soup.find(name='div',
                                class_=['op_mobilephone_r c-gap-bottom-small'])
            address = address.find_all('span')[-1]
            address = address.text.replace(' ', '-')
        else:
            address = ''
        self.data['address'] = address

    def get_label_type(self):
        """获取标记类型"""

        soup = BeautifulSoup(self.html, 'lxml')
        label_type = soup.find(name='div',
                               class_=['op_fraudphone_row'])
        if label_type:
            label_type = label_type.find_all('span')
            if len(label_type) > 2:
                label_type = label_type[0].text.strip()
            else:
                label_type = ''
        else:
            label_type = soup.find(name='h3',
                                   class_=['t c-gap-bottom-small'])
            if label_type:
                label_type = label_type.text.strip()
            else:
                label_type = ''

        self.data['label_type']= label_type

    def get_label_info(self):
        """获取标记信息，包括标记用户、标记数、标记"""

        soup = BeautifulSoup(self.html, 'lxml')
        description = soup.find(name='div',
                                class_='op_fraudphone_word')
        if description:
            description_text = description.text.strip()
            try:
                label_user = re.search('个(.*?)用户',
                                       description_text, re.S).group(1)
            except:
                label_user = ''
            try:
                label_number = re.search('被(.*?)个',
                                         description_text, re.S).group(1)
            except:
                label_number = ''
            try:
                label = re.search('标记为"(.*?)"',
                                  description_text, re.S).group(1)
            except:
                label = ''

            self.data['label_user'] = label_user.strip()
            self.data['label_number'] = label_number.strip()
            self.data['label'] = label.strip()

    def get_source_url(self):
        """获取标记来源网址"""

        soup = BeautifulSoup(self.html, 'lxml')
        source_url = soup.find(name='span', class_='c-showurl')
        if source_url:
            source_url = source_url.text
        else:
            source_url = ''
        self.data['source_url'] = source_url

    def get_abstract(self):
        """获取摘要信息"""

        soup = BeautifulSoup(self.html, 'lxml')
        abstract = soup.find(name='div', class_='op_fraudphone_word')
        if abstract:
            abstract = abstract.text
        else:
            abstract = ''

        self.data['abstract'] =abstract.strip().replace(' ', '"')

class HaosouHtml(Phone):
    """解析好搜的html"""

    def __init__(self, html):
        super(HaosouHtml, self).__init__()  # 继承父类init
        self.html = html
        self.data['engine'] = '好搜'

    def get_address(self):
        """获取号码所属地区"""

        soup = BeautifulSoup(self.html, 'lxml')
        address = soup.find(name='div',
                            class_=['gclearfix mh-detail'])
        if not address:
            address = soup.find(name='p',
                                class_=['mh-detail'])
        if address:
            address = address.text.strip()
            address = address.split('  ')
            if len(address) > 1:
                address = address[1].strip().replace('\t',
                                                     '').replace('\n', '-')
            else:
                address = ''
        else:
            address = ''

        self.data['address'] = address

    def get_label_type(self):
        """获取标记类型，诈骗或客服"""

        soup = BeautifulSoup(self.html, 'lxml')
        label_type = soup.find(name='span',
                               class_=['mohe-ph-mark'])
        if label_type:
            label_type = label_type.text
        else:
            label_type = soup.find(name='h3',
                                   class_=['title'])
            if label_type:
                label_type = label_type.text.strip()
            else:
                label_type = ''

        self.data['label_type'] = label_type.strip()

    def get_label_info(self):
        """获取标记信息，包括标记用户、标记数、标记"""

        soup = BeautifulSoup(self.html, 'lxml')
        frame = soup.find(name='div',
                                class_='cont mohe-wrap')
        if frame:
            description_text = frame.text.strip()
            try:
                label_user = re.search('位(.*?)用户',
                                       description_text, re.S).group(1)
            except:
                label_user = ''
            try:
                label_number = re.search('被(.*?)位',
                                         description_text, re.S).group(1)
            except:
                label_number = ''
            try:
                label = re.search('疑似为(.*?)！',
                                  description_text, re.S).group(1)
            except:
                label = ''

            self.data['label_user'] = label_user.strip()
            self.data['label_number'] = label_number.strip()
            self.data['label'] = label.strip()

    def get_source_url(self):
        """获取标记来源网址"""

        soup = BeautifulSoup(self.html, 'lxml')
        source_url = soup.find(name='a', class_='mohe-sjws')
        if source_url:
            source_url = source_url['href']
        else:
            source_url = ''
        self.data['source_url'] = source_url.strip()

    def get_abstract(self):
        """获取摘要信息"""

        soup = BeautifulSoup(self.html, 'lxml')
        frame = soup.find(name='div',
                          class_='cont mohe-wrap')
        if frame:
            abstract = frame.text.replace('\t',
                                           '').replace('\n', '').split('  ')
            abstract = abstract[-1]
            if '来自' in abstract:
                self.data['label_type'] = '图片'
            abstract = abstract.replace('“”', '“***”').replace('此','，此')
        else:
            abstract = ''

        self.data['abstract'] =abstract

    def get_tip(self):
        """获取友情提示，好搜有，百度好像没有。"""

        soup = BeautifulSoup(self.html, 'lxml')
        tip = soup.find(name='p', class_='mh-jingshi-tip')
        if tip:
            tip = tip.text
        else:
            tip = ''
        self.data['tip'] = tip.strip()

def parse(html_args):
    """

    :param html_args: dict must have 4 keys
    customer_id:
    phone:
    engine:
    html:
    status:
    :return: dict have 13 keys
    """

    if html_args['engine'] == 'baidu':
        parse_html = BaiduHtml(html=html_args['html'])
        exe = ['get_address', 'get_label_type', 'get_label_info',
               'get_source_url', 'get_abstract']
    else:
        parse_html = HaosouHtml(html=html_args['html'])
        exe = ['get_address', 'get_label_type', 'get_label_info',
               'get_source_url', 'get_abstract', 'get_tip']
    for each in exe:
        getattr(parse_html, each)()
    parse_html.data['status'] = html_args['status']
    parse_html.data['customer_id'] = html_args['customer_id']
    parse_html.data['phone'] = html_args['phone']
    return parse_html.data

def multi_parse(html_args, processes=1):
    """

    :param html_args: list
    :param processes: number
    :return: list
    """
    pool = Pool(processes)
    result_list = pool.map(parse, html_args)
    # df_list = [pd.DataFrame.from_dict(x, orient='index').T for x in result_list]
    # result_df = pd.concat(df_list, ignore_index=True)
    pool.close()
    pool.join()
    return result_list


if __name__ == '__main__':
    from http_requests import search
    args = {'customer_id':'13131-123151', 'phone': '01064658612'}
    htmls = search(args=args)
    for each in htmls:
        data = parse(each)
