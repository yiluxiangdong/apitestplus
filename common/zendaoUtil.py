# -*- coding: utf-8 -*-
# D:\autoTest\sunwoda\common\zendaoUtil.py
import requests
from time import strftime
import logging
import pandas as pd
logger = logging.getLogger(__name__)

def stampTodate(timestamp):
    ts = pd.Timestamp(timestamp)
    return str(ts.date())

def readexcelcase(path, index):
    df = pd.read_excel(path, skiprows=1, sheet_name=index)
    datas = df.to_dict('records')
    result = []
    for i in datas:
        user = {
            'account': i['account'], 'password': i['password']
        }
        projectInfo = {
            'project': i['project'], 'version': i['version']
        }
        data = {
            "name": i['name'],
            "assignedTo": [i['assignedTo']],
            "type": i['type'],
            "estimate": i['estimate'],
            "estStarted": stampTodate(i['estStarted']),
            "deadline": stampTodate(i['deadline'])
        }
        updatedate = {
            "currentConsumed": i['currentConsumed'],
            "assignedTo": i['assignedTo2'],
            "realStarted": str(pd.Timestamp(i['realStarted'])),
            "finishedDate": str(pd.Timestamp(i['finishedDate'])),
            "comment": i['comment']
        }
        result.append(
            {"host": i.get('host'), "projectInfo": projectInfo, "user": user, "data": data, "updatedate": updatedate})
    return result

def readexcelcaseplus(path, index):
    df = pd.read_excel(path, skiprows=1, sheet_name=index)
    datas = df.to_dict('records')
    result = []
    for i in datas:
        user = {
            'account': i['account'], 'password': i['password']
        }
        projectInfo = {
            'project': i['project'], 'version': i['version']
        }
        data = {
            "name": i['name'],
            "assignedTo": [i['account']],
            "type": 'test',
			"pri": 1,
            "estimate": i['timeConsume'],
            "estStarted": stampTodate(i['finishDate']),
            "deadline": stampTodate(i['finishDate'])
        }
        updatedate = {
            "currentConsumed": i['timeConsume'],
            "assignedTo": i['account'],
            "realStarted": str(pd.Timestamp(i['StartedTime'])),
            "finishedDate": str(pd.Timestamp(i['finishedTime'])),
            "comment": f"{i['name']}任务已完成"
        }
        result.append(
            {"projectInfo": projectInfo, "user": user, "data": data, "updatedate": updatedate})
    return result

class zendaodb:
    # def __init__(self,base_cnf,env):
    #     self.conf = base_cnf
    #     self.env = env
    #     if self.env == 'test':
    #         name = 'zentao_test'
    #     else:
    #         name = 'zentao'
    #     self.zentao = [{'user':v['account'][0]['user'],'host':v['host']} for k,v in self.conf.items() if k == name][0]
    #     self.user = self.zentao['user']
    #     self.host = self.zentao['host']
    def __init__(self,user):
        ##
        self.host = r'http://zentao.sunwoda.com/'
        self.user = user

    def session(self):
        logger.info('登录禅道')
        s = requests.Session()
        token = s.post(url=f'{self.host}/zentao/api.php/v1/tokens', json=self.user, verify=False).json()
        s.headers.update(token)
        return s

    def getproduct(self, name):  # 获取产品ID
        res = self.session().get(url=f'{self.host}/zentao/api.php/v1/products').json()
        reslist = [{'id': i['id'], 'program': i['program'], 'name': i['name'], 'code': i['code']} for i in
                   res['products']]
        logger.info(f'禅道bug提交完成  {reslist}')
        return [project['id'] for project in reslist if project['name'] == name][0]

    def createBUG(self, interfaceName: str, body: dict):
        names = interfaceName.split("_")
        url = f'{self.host}/zentao/api.php/v1/products/{self.getproduct(names[0])}/bugs'
        title = f"【测试环境】场景{interfaceName}{strftime('%Y%m%d%H%M%S')}接口异常"
        datas = {
            "title": f"{title}",
            "severity": 1,
            "pri": 1,
            "steps": f'''
                <p>【所属模块】</p>\n<p>{names[1]}</p>\n<br />\n
                <p>【请求场景】</p>\n{interfaceName}<br />\n
                <p>【请求地址】</p>\n{body['api']}<br />\n
                <p>【返回结果】</p>\n{body['result']} <br />
              ''',
            "type": "codeerror",
            "deadline": strftime('%Y-%m-%d %H:%M:%S'),
            "openedBuild": [
                "trunk"
            ]
        }
        logger.info('禅道bug提交完成')
        self.session().post(url=url, json=datas, verify=False).json()

    def __del__(self):
        pass

    def project(self, projectName=''):  # 获取产品ID
        data = self.session().get(url=f'{self.host}/zentao/api.php/v1/projects').json()['projects']
        for item in data:
            if item['name'] == projectName:
                return item['id']

    def version(self, projectId, versionName):  # 获取版本ID
        executions = self.session().get(url=f'{self.host}/zentao/api.php/v1/projects/{projectId}/executions').json()[
            'executions']
        for item in executions:
            if versionName in item['name']:
                return item['id']

    def addtask(self, tasks, datas):  # 获取产品ID
        return self.session().post(url=f'{self.host}/zentao/api.php/v1/executions/{tasks}/tasks', json=datas).json()

    def updatetask(self, tasks, datas):  # 修改任务状态
        return self.session().post(url=f'{self.host}/zentao/api.php/v1/tasks/{tasks}/finish', json=datas).json()

    def createTask(self, types, projectname, versionName, datas, updatedata):  # false-创建  true -更新完成
        taskId = self.addtask(self.version(self.project(projectname), versionName), datas)
        if taskId.get("id"):
            if types == True:
                self.updatetask(taskId.get("id"), updatedata)
                return {'msg': "任务完成更新成功", 'date': taskId}
            else:
                return {'msg': "任务创建成功", 'date': taskId}
        else:
            return {'msg': "任务创建失败", 'date': taskId}


    def getTaskList(self,executions,taskName):
        result = []
        tasklist = self.session().get(url=f'{self.host}/zentao/api.php/v1/executions/{executions}/tasks').json().get("tasks")
        for task in tasklist:
            if task['name'] == taskName:
                result.append(task['id'])
        return result

    def deleteTask(self, taskId):  # false-创建  true -更新完成
        self.session().delete(url=f'{self.host}/zentao/api.php/v1/tasks/{taskId}').json()
        return {'msg':f'任务：{taskId}删除成功'}




if __name__ == '__main__':
    # datas = readexcelcase(r'../files/zentaoTask.xlsx', 0)
    # print(datas)

    host = 'http://192.168.12.79:8899/'
    user = {
        "account": "test",
         "password": "111111"
    }
    # host = 'http://zentao.sunwoda.com'
    # user = {
    #     "account": "liuxiaobing",
    #     "password": "123456"
    # }
    zd = zendaodb(user)
    data = {
        "name": "已归档和未归档合同能生成清单，并且可以导出报表3",
        "assignedTo": [user['account']],
        "type": "devel",
        "estimate": 4,  # 预计工时
        "estStarted": "2024-08-23",
        "deadline": "2024-08-23"
    }
    updatedate = {
        "currentConsumed": 4,  # 实际工时
        "assignedTo": user['account'],
        "realStarted": "2024-08-23 08:00:00",
        "finishedDate": "2024-08-23 12:00:00",
        "comment": "完成任务"
    }
    # print(zd.project('EHS综合管理平台'))
    #通过名称获取需要删除的taskID
    task= zd.getTaskList(zd.version(zd.project('EHS综合管理平台'),'测试执行1'),'已归档和未归档合同能生成清单，并且可以导出报表98')
    for id in task:
        print(zd.deleteTask(id))







    # print(zd.createTask(True,'EHS综合管理平台','测试执行1',data,updatedate))
    # # print(zd.addtask(zd.version(zd.project('CRM二期'),'0831版本'),data))
    # taskid = zd.addtask(zd.version(zd.project('EHS综合管理平台'), '测试执行1'), data)
    # print(taskid)
    # print(zd.updatetask(taskid,updatedate))


















