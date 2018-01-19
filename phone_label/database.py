# -*- coding: utf-8 -*-

import os
import time
import cx_Oracle
import pandas as pd
from sqlalchemy import create_engine
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'   # 防止插入数据时变问号

USERNAME = '********'
PASSWORD = '********'
HOST = '********'
PORT = '********'
SID = '********'



# 数据输出的表名
OUTPUT_TABLE = 'phone_label'

class Connect:
    """"""
    def __init__(self, db):
        """"""
        if db.upper() == 'ORACLE':
            # self.engine = create_engine(
            #     'oracle://%s:%s@%s:%s/%s' % (
            #     USERNAME, PASSWORD, HOST, PORT, SID))

            self.engine = cx_Oracle.connect(
                USERNAME, PASSWORD, '%s:%s/%s' % (HOST, PORT, SID)
            )

    def read_sql(self, sql):
        """"""
        data_frame = pd.read_sql(sql=sql, con=self.engine)
        return data_frame

    def write_sql(self, data, table):
        """"""
        # data.to_sql(table, self.engine, if_exists='append', index=False,
        #             schema='lijianbin')

        sql = """insert into %s values (:ID, :CUSTOMER_ID, :PHONE, :ADDRESS, 
:ENGINE, :LABEL_USER, :LABEL_NUMBER, :LABEL_TYPE, :LABEL, :TIP, :SOURCE_URL, :ABSTRACT, :CREATE_TIME, :STATUS)""" % table
        cursor = self.engine.cursor()
        cursor.prepare(sql)
        cursor.executemany(None, data)
        self.engine.commit()
        cursor.close()




    def get_maxID(self, table):
        """获取表中最大的ID号"""

        sql = 'select max(id) MAX_ID from %s' % table
        data_frame = pd.read_sql(sql=sql, con=self.engine)
        max_id = data_frame['MAX_ID']

        return max_id

    def add_index(self, data):
        """"""

        max_id = self.get_maxID(OUTPUT_TABLE)[0]
        if not max_id:
            max_id = 0
        local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        for i in range(len(data)):
            data[i]['id'] = int(max_id + i + 1)
            data[i]['create_time'] = local_time
        # data['id'] = pd.Series(data.index + max_id + 1)
        # local_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # data['create_time'] = pd.Series([local_time] * data.shape[0])
        return data


if __name__ == '__main__':
    sql ='SELECT customer_id, fix_phone FROM guhua_1 where key>3350 and key<3401'
    db = Connect('oracle')
    data = db.read_sql(sql)
    pass