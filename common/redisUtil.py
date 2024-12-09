# -*- encoding:utf-8 -*-
#D:\autoTest\sunwoda\common\redisUtil.py
import redis
import logging
import datetime
import json
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            print("MyEncoder-datetime.datetime")
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        if isinstance(obj, int):
            return int(obj)
        elif isinstance(obj, float):
            return float(obj)
        elif isinstance(obj, object):
            return str(obj)
        elif isinstance(obj, list):
           return str(obj)
        elif obj is None:
            return str("")
        else:
            return super(MyEncoder, self).default(obj)


class RedisUtil:
    def __init__(self, host, port, password=None):
        self.logger = logging.getLogger(__name__)
        self.pool = redis.ConnectionPool(host=host, port=port, password=password, decode_responses=True)
        self.logger.info('初始化连接redis服务')
        self.r = redis.StrictRedis(connection_pool=self.pool)


    def savedict(self, keys: str, data, msg: str):
        # self.logger.info(f"保存{msg}到缓存中----->{keys}:{json.dumps(data,ensure_ascii=False,indent=2)}")
        try:
            self.logger.info(f"保存{msg}到缓存中----->{keys}:{data}")
            if isinstance(data,dict):
                if self.r.exists(keys):
                    initdata = json.loads(self.r.get(keys))
                    initdata.update(data)
                else:
                    initdata = data
                self.r.set(keys, json.dumps(initdata, cls=MyEncoder, indent=4))
            elif isinstance(data,list):
                #self.r.setex() 设置有效期 
                json_data_list = [json.dumps(item, ensure_ascii=False, indent=4) for item in data]
                self.r.lpush(keys, *json_data_list)
        except Exception as e:
            self.logger.info(f"写入缓存失败：{e}")

    def getdata(self, key):
        self.logger.info(f"从缓存中获取{key}对应的值")
        if self.r.exists(key):
            if self.r.type(key) == 'list':
                return self.r.lrange(key, 0, -1)
            return json.loads(self.r.get(key))

    def getkeys(self):
        return self.r.keys()

    def deldate(self, key=None):
        if key:
            if self.r.exists(key):
                self.logger.info(f"从缓存中删除{key}对应的值")
                self.r.delete(key)
        else:
            for keys in self.r.keys():
                self.logger.info(f"从缓存中删除{str(keys, 'utf-8')}对应的值")
                self.r.delete(str(keys, 'utf-8'))



if __name__ == '__main__':
    Redis = RedisUtil('192.168.12.79', 6380, '123456')
    print(Redis.getkeys())
