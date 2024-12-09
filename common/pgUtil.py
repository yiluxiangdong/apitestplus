# -*- encoding:utf-8 -*-
import psycopg2
class pgDB:
    def __init__(self,database):
        # 测试环境
        # self.conn = psycopg2.connect(
        #     host="172.21.127.168",  # 数据库服务器地址
        #     database=database,  # 数据库名
        #     user="swdcrm",  # 数据库用户名
        #     password="Swd.!0518_Crm",  # 数据库密码
        #     port="2345"  # 数据库端口，默认为5432
        # )
       #服务器
        self.database = database
        self.conn = psycopg2.connect(
            host="192.168.12.79",  # 数据库服务器地址
            database=self.database,  # 数据库名
            user="test",  # 数据库用户名
            password="111111",  # 数据库密码
            port="5432"  # 数据库端口，默认为5432
        )
        # 创建一个游标对象
        self.cur = self.conn.cursor()

    def selectcasedb(self):
       self.cur.execute(f"SELECT *  FROM t_apitest_file WHERE filetype='1';")
       columns = [desc[0] for desc in self.cur.description]
       rows = self.cur.fetchall()
       dict_list = []
       for row in rows:
           dict_list.append(dict(zip(columns, row)))
       
       for case in dict_list:
           case['index']= dict_list.index(case)+1
       return dict_list


    def selectdb(self):
       self.cur.execute(f"SELECT *  FROM t_apitest_file")
       columns = [desc[0] for desc in self.cur.description]
       rows = self.cur.fetchall()
       dict_list = []
       for row in rows:
           dict_list.append(dict(zip(columns, row)))
       return dict_list

    def selectdbFilename(self,filename):
       self.cur.execute(f"SELECT *  from t_apitest_file WHERE filename='{filename}';")
       columns = [desc[0] for desc in self.cur.description]
       rows = self.cur.fetchall()
       dict_list = []
       for row in rows:
           dict_list.append(dict(zip(columns, row)))
       return dict_list


    def insertdata(self,*args):
        try:
            sql = f"INSERT INTO t_apitest_file (fileurl, filename,filetype, filesize, realfilename,createtime,updatetime) VALUES {(args)}"
            self.cur.execute(sql)
            self.conn.commit()
            return {'msg':"上传成功"}
        except Exception as e:
            return {'msg': e.args[0]}

    def updatedata(self,filename,updatetime,url):
        try:
            sql = f"update t_apitest_file set updatetime = '{updatetime}', fileurl='{url}'   WHERE filename='{filename}';"
            self.cur.execute(sql)
            self.conn.commit()
            return {'msg':"上传成功"}
        except Exception as e:
            return {'msg': e.args[0]}

    # #新增case
    # def insertcase(self,*args):
    #     try:
    #         sql = "INSERT INTO t_apitest_case(interfacename,function, systemname,level,loop,method, module, role,url,body,save_key,asserts,createtime,updatetime) VALUES (%s,%s, %s,%s,%s,%s, %s, %s,%s,%s,ARRAY%s,ARRAY%s,%s,%s)"
    #         self.cur.execute(sql, (args))
    #         return {'msg':"提交成功"}
    #
    #     except Exception as e:
    #         return {'msg': e.args[0]}

    # 新增case  i['index'],i['filename']
    def insertcase(self, interfacename, function, systemname, level, loop, method, module, role, url, body, save_key,asserts, createtime, updateTime,index,filename):
        try:
            sql = f"INSERT INTO t_apitest_case(interfacename,function, systemname,level,loop,method, module, role,url,body,save_key,asserts,createtime,updatetime,index,filename) VALUES ('{interfacename}','{function}', '{systemname}','{level}','{loop}','{method}', '{module}', '{role}','{url}','{body}',ARRAY{save_key},ARRAY{asserts},'{createtime}','{updateTime}','{index}','{filename}')"
            self.cur.execute(sql)
            return {'msg': "提交成功"}

        except Exception as e:
            return {'msg': e.args[0]}



    #更新case
    def updatecase(self,interfacename,module,function,level,systemname,role,loop,url,method,body,save_key,asserts,updatetime,index,filename,):
        try:
            sql = f"UPDATE t_apitest_case SET module = '{module}',function = '{function}',level = '{level}',systemname = '{systemname}',role = '{role}',index = '{index}',loop = '{loop}',filename = '{filename}',url = '{url}',method = '{method}',body = '{body}',save_key = ARRAY{save_key},asserts = ARRAY{asserts},updatetime = '{updatetime}' where interfacename = '{interfacename}';"
            self.cur.execute(sql)
            self.conn.commit()
            return {'msg':"更新成功"}
        except Exception as e:
            return {'msg': e.args[0]}



    def selectcasename(self,interfacename):
       self.cur.execute(f"SELECT  *  from t_apitest_case WHERE interfacename = '{interfacename}';")
       columns = [desc[0] for desc in self.cur.description]
       rows = self.cur.fetchall()
       dict_list = []
       for row in rows:
           dict_list.append(dict(zip(columns, row)))
       return dict_list





    def updateDB(self,id):
        self.cur.execute(f"update contract.c_contract_review set risk_status=1 WHERE contract_id = '{id}';")
        self.conn.commit()
    
    def updatesale(self,customers):
       '''
       修改订单履行专员
       '''
       self.cur.execute(f"update customer.c_customer_base_information set order_perform_commissioner_name ='刘小兵',order_perform_commissioner_no='1603089673950240769' WHERE customer_name = '{customers}';") 
       self.conn.commit()


    def __del__(self):
        # 关闭游标和连接
        self.conn.commit()
        self.cur.close()
        self.conn.close()

if __name__ == '__main__':
    pg = pgDB('apitest')
    for i in pg.selectdb():
        print(i)
    