# -*- encoding:utf-8 -*-
#D:\autoTest\sunwoda\common\mongoUtil.py
import pymongo
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    def __init__(self, conf):
        logger.info(f'连接mongodb数据库')
        self.conf = conf
        # self.client = pymongo.MongoClient(host=self.conf['host'], port=self.conf['port'], username=None, password=None)
        self.client = pymongo.MongoClient(**conf)
        # self.client = pymongo.MongoClient("mongodb://192.168.12.79:27017/")
        self.db = self.client['apitest']
        # self.collection = self.db[self.databasename]

    def insertdata(self, data: dict, databasename):
        # 向集合插入一条数据
        collection = self.db[databasename]
        collection.insert_one(data)

    def selectalldata(self, databasename):
        # 查询集合中所有数据
        collection = self.db[databasename]
        return [data for data in collection.find()]

    def cleandata(self, databasename):
        # 删除所有的数据
        collection = self.db[databasename]
        collection.drop()

    def cleanalldata(self, tablelist, flag=False):
        res = []
        for i in tablelist:
            if flag:
                self.cleandata(i)
            res.append({i: self.selectalldata(i)})
        return res

    def __del__(self):
        pass

        # print(self.client.list_database_names())
        # self.client.close()


if __name__ == '__main__':
    conf = {
        'host': '192.168.12.79',
        'port': 27017
    }



