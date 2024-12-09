# -*- encoding:utf-8 -*-
import psycopg2
from sympy.polys.dispersion import dispersion


class pgDB:
    def __init__(self,database):
        # 测试环境
        self.conn = psycopg2.connect(
            host="172.21.127.168",  # 数据库服务器地址
            database=database,  # 数据库名
            user="swdcrm",  # 数据库用户名
            password="Swd.!0518_Crm",  # 数据库密码
            port="2345"  # 数据库端口，默认为5432
        )
       #服务器
        self.database = database
        # self.conn = psycopg2.connect(
        #     host="192.168.12.79",  # 数据库服务器地址
        #     database=self.database,  # 数据库名
        #     user="test",  # 数据库用户名
        #     password="111111",  # 数据库密码
        #     port="5432"  # 数据库端口，默认为5432
        # )
        # 创建一个游标对象
        self.cur = self.conn.cursor()


    def updateDB(self,id):
        self.cur.execute(f"update contract.c_contract_review set risk_status=1 WHERE contract_id = '{id}';")

        "update contract.c_contract_basic_info set  status = 4 WHERE contract_code='XZW-CO202411250009';"
        self.conn.commit()

    def updatecontract(self,code,status):
        self.cur.execute(f"update contract.c_contract_basic_info set  status = {status} WHERE contract_code='{code}';")
        self.conn.commit()


    def updatesale(self,customers):
       '''
       修改订单履行专员
       '''
       self.cur.execute(f"update customer.c_customer_base_information set order_perform_commissioner_name ='刘小兵',order_perform_commissioner_no='1603089673950240769' WHERE customer_name = '{customers}';") 
       self.conn.commit()

    def updateprojectlevel(self,code,level):
        self.cur.execute(f"update crmopportunity.c_opp_follow_up set  project_level = '{level}' WHERE opp_code='{code}';")
        self.conn.commit()


    def __del__(self):
        # 关闭游标和连接
        self.conn.commit()
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    pg = pgDB('crmcontract')
    pg.updatecontract('XZW-CO202411250009', 5)