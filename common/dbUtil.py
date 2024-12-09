# -*- encoding:utf-8 -*-
#D:\soft\pycharm\project\sunwoda\common\dbUtil.py
import json
from itertools import chain
from time import strftime, localtime
import pymysql
from common.commomUtil import computer_information
import logging
from dbutils.pooled_db import PooledDB
from common.commomUtil import read
logger = logging.getLogger(__name__)
class apitest:
    def __init__(self,conf):
        logger.info(f'连接mysql数据库')
        mysqlcnf = conf['db_mysql']
        POOL = PooledDB(
            creator=pymysql,
            maxconnections=6,
            blocking=True,
            ping=1,
            host=mysqlcnf['host'],
            port=mysqlcnf['port'],
            database=mysqlcnf['database'],
            user=mysqlcnf['user'],
            password=mysqlcnf['password'],
            charset="utf8"
        )
        try:
            self.db = POOL.connection()
            # logger.info(f'连接MongoDB数据库')
            # Mongocnf = conf["MongoDB"]
            # Mongocnf.pop("desc")
            # self.mongo = MongoDB(Mongocnf)
            self.cursor = self.db.cursor()  # 获取游标
            # self.cursor.execute("SET SESSION MAX_EXECUTION_TIME=100")
            self.hostinfo = computer_information()
            self.cleandata()
            self.all_executed_test_cases()
            self.current_executed_test_cases()
        except Exception as e:
            logger.info(f'连接MongoDB/mysql数据库失败：{e}')

    def cleandata(self):
        tablelist = ["t_apitest_casename", "t_apitest_current_bug", "t_apitest_current_case",
                     "t_apitest_current_implement", "t_apitest_current_passrate", 't_apitest_current_result_1122']
        for table in tablelist:
            logger.info(f'清空mongodb中{table}表中的数据')
            # self.mongo.cleandata(table)
            logger.info(f'清空{table}表中的数据')
            self.cursor.execute(f"truncate table  {table}")

    def exec_insert(self, tables: list, params: list, hostinfo=None):
        # '''
        # 封装执行语句
        # '''
        logger.info(f'将数据写入mysql数据库表{tables}中')
        # logger.info(f'将数据写入MongoDB数据库表{tables}中')
        for data in params:
            if hostinfo and isinstance(data, dict):
                data.update(self.hostinfo)
            keylist = str(list(data.keys())).strip('[]').replace("'", '')
            valueslist = str(list(data.values())).strip('[]')
            try:
                for table in tables:
                    # self.mongo.insertdata(data,table)
                    self.cursor.execute(f"INSERT INTO {table}({keylist}) VALUES({valueslist})")
                    self.db.commit()
            except Exception as e:
                self.db.rollback()
                return e
    def exec_insert_result(self, tables: list, params: list):
        # '''
        # 封装执行语句
        # '''
        logger.info(f'将数据写入mysql数据库表{tables}中')
        for data in params:
            if self.hostinfo and isinstance(data, dict):
                data.update(self.hostinfo)
            keylist = str(list(data.keys())).strip('[]').replace("'", '')
            valueslist = str(list(data.values())).strip('[]')
            try:

                for table in tables:
                    self.cursor.execute(f"INSERT INTO {table}({keylist}) VALUES({valueslist})")
                    self.db.commit()
            except Exception as e:
                logger.info(f'将数据写入mysql数据库表{tables}失败：{e}')
                self.db.rollback()
                return e

    def save_case_result(self, params: list):
        # '''
        # 保存测试结果
        # '''
        logger.info(f'将数据写入params数据库表中  {params}')
        self.exec_insert(['t_apitest_result_1122', 't_apitest_current_result_1122'], params)

    def save_pass_rate(self, params: list):
        # '''
        # 保存用例通过率数据
        # '''
        self.exec_insert(['t_apitest_passrate', 't_apitest_current_passrate'], params, self.hostinfo)

    def error_summary(self, params: list):
        # '''
        # 保存bug汇总结果
        # '''
        self.exec_insert(['t_apitest_bug', 't_apitest_current_bug'], params, self.hostinfo)

    def current_executed_test_result(self, params: list):
        # '''
        # 保存用例执行详情
        # '''
        self.exec_insert(['t_apitest_implement', 't_apitest_current_implement'], params, self.hostinfo)

    def all_executed_test_cases(self):
        # """
        # 读取测试用例
        # """
        read(r'config/casepath.yaml')
        CASE_PATH_FILE = read(r'config/casepath.yaml')
        params = list(chain(*[
            [{"filename": k, "casename": i, "createtime": strftime('%Y-%m-%d  %H:%M:%S', localtime())} for i in v]
            for k, v in CASE_PATH_FILE.items()]))
        self.exec_insert(['t_apitest_casename'], params)

    def current_executed_test_cases(self):
        # """
        # 读取测试用例
        # """
        CONF_CASENAME_FILE = read(r'config/casename.yaml')
        params = list(chain(*[
            [{"platform": k, "interfaceName": i, "createtime": strftime('%Y-%m-%d  %H:%M:%S', localtime())} for i in v]
            for k, v in CONF_CASENAME_FILE.items()]))
        self.exec_insert(['t_apitest_current_case'], params, self.hostinfo)

    def get_report_detaill(self,keyId,project):
        self.cursor.execute(f"SELECT detaill,result,keyId from t_api_result_all_v1   where keyId='{keyId}' and project='{project}'")
        data = self.cursor.fetchone()
        return {'data':json.loads(data[0]),"result":json.loads(data[1]),"keyId":data[2]}


    def __del__(self):
        logger.info(f'关闭数据库')
        self.db.close()


if __name__ == "__main__":
    conf = read(r'../config/base.yaml')
    apitest = apitest(conf)
    data = apitest.get_report_detaill('20240305145019','OTD系统')
    print(data)






