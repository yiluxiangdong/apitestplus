# -*- encoding:utf-8 -*-
import requests
from common.commomUtil import HTTP, logger
from common.commomUtil import read
from common.getToken import gettoken

#单个用例测试结果反馈
def apitestcase(project,datas):
    # try:
    #     cnf = read(r'..\config\config.yaml')[project]
    # except:
    #     cnf = read(r'.\config\config.yaml')[project]
    cnf = read(r'../config/config.yaml')[project]
    host = cnf['host']
    account = cnf['account']
    if isinstance(account,list):
        data = list(cnf['account'][0].values())[0]
    else:
        data = cnf['account']
    session = requests.Session()
    session.headers.update(gettoken(project, data))
    result = getattr(HTTP(logger), str(datas.get('method')).lower())(session, url=host+datas["url"], data=datas["body"])
    return  result

if __name__ == '__main__':
    datas = {
        "url": "/api/crm-info/activity/list", 
        "method": "post",
        "body": {"size": 20, "num": 1, "userIdList": []}
    }
    print(testcase('project_crm',datas))


