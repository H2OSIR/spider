# -*- coding:utf-8 -*-
"""定时任务，包括定时获取代理IP，定时从数据库获取参数。

"""
import re
import time
import sched
import traceback
import logging
from os import listdir
from run import start, sql
from logging.handlers import TimedRotatingFileHandler


# 日志文件名
def LOG_NAME():
    """返回日志文件名"""
    log_name = time.strftime("log/%Y-%m-%d.log", time.localtime())
    return log_name

logger = logging.getLogger('timming_tasks')
logging.basicConfig(filename=LOG_NAME(),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

s = sched.scheduler(time.time, time.sleep)


class Schedual:
    """定时任务"""
    def __init__(self, args_count):
        """每次需要查询 args_count 个参数

        :param args_count: 参数个数
        """
        self.args = args_count
        # 声明全局变量记录异常次数，当连续异常次数达到5次，则退出python程序
        self.error_count = 0

    def generate_sql(self):
        """解析记录文件，得出最近依次执行的sql，并生成新的sql。"""

        with open('log/record_sql.log', 'r+') as f:
            s = f.read()
            if s:
                sqls = re.findall('SQL="(.*?)"', s, re.S)
                if sqls:
                    end_row = re.search('key<(.*?);', sqls[-1], re.S).group(1)
                else:
                    end_row = 1
            else:
                end_row = 1
            f.close()
        new_sql = sql(int(end_row) - 1, int(end_row) + self.args - 1)
        return new_sql

    def start_task(self):
        """任务主程序"""
        print('-----start-----')
        sql = self.generate_sql()
        try:
            start(sql=sql)
            with open('log/record_sql.log', 'a+') as f:
                f.write('\n[%s]: SQL="%s;"' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),sql))
                f.close()
            self.error_count = 0
        except Exception as e:
            self.error_count += 1
            logger.error(traceback.format_exc())
            time.sleep(30)
            if self.error_count == 10:
                quit()
        s.enter(10, 0, self.start_task, ())

    def run(self):
        """启动定时任务"""
        s.enter(0, 0, self.start_task, ())
        s.run()

if __name__ == '__main__':

    schedual = Schedual(50)
    schedual.run()
    # 每次查询500条记录


