# -*- encoding:utf-8 -*-
#D:\autoTest\sunwoda\conftest.py
import configparser
import inspect
import logging
import time
from collections import defaultdict
from pydoc import html
import allure
import requests
from _pytest.assertion.util import assertrepr_compare
import pytest
from time import strftime
from jsonpath import jsonpath
from py._xmlgen import html
import random
# from py.xml import html
from common.getToken import srm_token, dianlian_token, gettoken
from common.commomUtil import get_request_parameters, init_time_args, read, write, updateTemp
from faker import Faker
from  common.redisUtil import RedisUtil as r
logger = logging.getLogger(__name__)

base_cnf = read(r'./config/base.yaml')
test_cnf = read(r'./config/config.yaml')
# configpath = getfile('config')
# base_cnf = read(f'{configpath}/base.yaml')
# test_cnf = read(f'{configpath}/config.yaml')


fake = Faker(locale='zh_CN')
redis_cnf = base_cnf['db_redis']
# Redis = r(redis_cnf['host'],redis_cnf['port'],redis_cnf['password']) if redis_cnf['enable'] else False
Redis = r(redis_cnf['host'],redis_cnf['port'],redis_cnf['password'])

initdatas = {
    "email": fake.free_email(),
    "phone": fake.phone_number(),
    "contactsName": fake.name(),
    "customerName": f"中国三六重工{str(random.randint(1, 99999)).rjust(5, '0')}分公司",
    "orgName": "欣智旺",
    "deptName": "销售二部",
    "contractName": f"合同{str(random.randint(1, 99999)).rjust(5, '0')}",
    "loginurl": 'https://crm-uat.sunwoda.com/login/',
    "starttime": strftime('%Y-%m-%d %H:%M:%S')
}

def casedata():
    updateTemp(r'./config/temp.yaml',initdatas)
    # initdatas.update({'datetimelist': init_time_args()})
    # # 降临时变量持久化到文件
    # write(r'.\config\temp.yaml', initdatas)
    if Redis:
        Redis.savedict('temp',initdatas,'保存临时变量到缓存中')
    return get_request_parameters(base_cnf)

def pytest_collection_modifyitems(items):
    """
    测试用例收集完成时，将收集到的item的name和nodeid的中文显示
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

##########################改造测试报告#################################
def pytest_html_results_table_html(report, data):
    if report.passed:
        del data[:]
        data.append(html.div("这条用例通过啦！", class_="empty log"))

def pytest_configure(config):
    marker_list = ["optionalhook", "hookwrapper"]  # 标签名集合
    for markers in marker_list:
        config.addinivalue_line(
            "markers", markers
        )
    conf = configparser.ConfigParser()
    confile = r'./pytest.ini'
    conf.read(confile)
    node = 'pytest'
    key = 'log_file'
    value = f'./log/apitest_{time.strftime("%Y%m%d")}.log'
    conf.set(node, key, value)
    fil = open(confile, 'w')  # 不能用wb
    conf.write(fil)  # 把要修改的节点的内容写到文件中
    fil.close()

    # config._metadata["项目名称"] = "接口自动化测试"
    # config._metadata["开始时间"] = start
    # try:
    #     sys_platform = platform.platform().lower()
    #     config._metadata.pop("JAVA_HOME")
    #     config._metadata.pop("Plugins")
    #     config._metadata.pop("Packages")
    #     if "linux" in sys_platform:
    #         config._metadata.pop("WORKSPACE")
    #         config._metadata.pop("JOB_NAME")
    #         config._metadata.pop("NODE_NAME")
    #         config._metadata.pop("CI")
    #         config._metadata.pop("EXECUTOR_NUMBER")
    #         config._metadata.pop("BUILD_URL")
    #         config._metadata.pop("BUILD_ID")
    #         config._metadata.pop("BUILD_NUMBER")
    #         config._metadata.pop("BUILD_TAG")
    # except FileNotFoundError as e:
    #     raise e


@pytest.mark.optionalhook
@pytest.hookimpl(optionalhook=True)
def pytest_html_results_summary(prefix):
    prefix.extend([html.p("所属部门: 信息中心")])
    prefix.extend([html.p("测试人员: 2204010095")])


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_header(cells):
    # cells.insert(3, html.th('用例耗时'))
    cells.insert(2, html.th('执行时间'))
    cells.insert(2, html.th('描述', class_='sortable time', col='time'))
    cells.pop()

# 修改测试结果 Results 中用例的表头
# @pytest.mark.optionalhook
# def pytest_html_results_table_row(report, cells):
#     cells.insert(2, html.td(report.description))  # 表头对应的内容
#     cells.insert(3, html.td(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), class_="col-time"))
#     cells.pop(-1)  # 删除link

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):  # Description取值为用例说明__doc__
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")

def pytest_html_report_title(report):
    report.title = f"接口自动化测试报告-{strftime('%Y-%m-%d')}"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
##########################改造测试报告#################################
def getToken(**kwargs):
    s = requests.session()
    logger.info(f'{kwargs}')
    # if jsonpath(base_cnf, f'$..{kwargs["project"]}')[0]['enable']:
    if base_cnf["project"]["system"][kwargs['project']]['enable']:
        if not  kwargs["account"].get('header'):
            if kwargs['project'] == 'project_crm': #调用获取登录账号所在的部门和组织ID
                try:
                    s.headers.update(gettoken('project_crm', kwargs['account']))
                except:
                    s.headers.update({"Deptid": "None", "Orgid": "None"})
            elif kwargs['project'] == 'project_srm':
                logger.info('project_crm', kwargs['account'])
                s.headers.update(gettoken('project_crm', kwargs['account']))

            elif kwargs['project'] == 'project_otd':
                head= {
                    "Business-Unit": "Sunwinon",
                    "Employeeno": str(kwargs['account']['username']),
                    "Role-Id": "1701522167466668033"
                }
                s.headers.update(head)
                s.headers.update(gettoken('project_otd', kwargs['account']))

            elif kwargs['project'] == 'project_mro':
                url = f'https://apitest.sunwoda.com/api/mroToken'
                body = kwargs['account']
                result = s.post(url,json=body).json()
                s.headers.update({'Authorization': f"Bearer {result.get('access_token')}"})
                s.headers.update({'X-Logined-Sign': result.get("username")})
                s.headers.update({'X-TenantId': str(result.get("tenantId"))})

            elif kwargs['project'] == 'project_meet':
                s.headers.update(gettoken('project_meet', kwargs['account']))
                url = f'{test_cnf["project_meet"]["host"]}/api-meeting-manager/user/getUserInfo'
                data = {
                    "appCode" : "c46b9bc98eba4d6ba0d79da2277133e1",
                    "queryEnterprise" : True,
                    "queryEnterpriseList" : True,
                    "queryEnterpriseUserInfo" : True,
                    "queryOrganization" : True,
                    "queryUserRole" : True
                }
                res = s.post(url, json=data).json()
                userId = jsonpath(res, f'$.datas.userId')
                s.headers.update({"X-Userid-Header": userId[0]})

            else:
                s.headers.update(kwargs['account'])
        else:
            s.headers.update(kwargs["account"]['header'])
        return s
@pytest.fixture(scope="session")
def sessions():
    dic = defaultdict(dict)
    sessionlist = []
    for k, v in enumerate(test_cnf):
        if not isinstance(test_cnf[v]['account'],list):
            sessionlist.append({test_cnf[v]['desc']: {base_cnf['default']['role']: getToken(account = test_cnf[v]['account'],project = v)}})
        else:
            for items in test_cnf[v]['account']:
                sessionlist.append({test_cnf[v]['desc']:{list(items.keys())[0]:getToken(account = list(items.values())[0],project = v)}})
    for i in sessionlist:
        dic[list(i.keys())[0]].update(list(i.values())[0])
    if Redis:
        Redis.savedict('session',dict(dic),'保存token到缓存中')
    return dict(dic)
# 返回结果
# {
#     "农业平台": {
#         "供应商": <requests.sessions.Session object at 0x000001F62EB6A0C8>,
#         "采购商": <requests.sessions.Session object at 0x000001F6315ECB48>
#     },
#     "EHS综合管理平台": {
#         "管理员": <requests.sessions.Session object at 0x000001F6312CA3C8>,
#         "副管理员": <requests.sessions.Session object at 0x000001F6311C3208>
#     },
#     "SRM管理平台": {
#         "供应商": <requests.sessions.Session object at 0x000001F631635248>,
#         "供应商2": <requests.sessions.Session object at 0x000001F6312E8E48>,
#         "采购商": <requests.sessions.Session object at 0x000001F631642448>,
#         "采购商2": <requests.sessions.Session object at 0x000001F631642EC8>,
#         "技术开发": <requests.sessions.Session object at 0x000001F631625E88>
#     },
#     "欣学堂": {
#         "管理员": None
#     }
# }


def pytest_assertrepr_compare(config, op, left, right):
    '''
    为断言添加自定义功能
    通过前面的介绍，感觉Pytest的assert挺完美了，又简单又清晰。但是在实际的测试工作中，还会遇到一些实际问题，比如在断言时，最好【自动】添加一些日志，避免我们在测试代码中手动加入日志。还有，最好能将断言的信息，【自动】集成到一些测试报告中，比如Allure中（关于Allure报告大家可以看之前的文章《用Pytest+Allure生成漂亮的HTML图形化测试报告》）。这样就能避免在每一个测试脚本中手动写很多重复的代码，从而让我们将更多的时间和精力放到编写测试用例上。
    有了这样的想法，接下来看看如何实现。
    Pytest中提供了一个Hook函数pytest_assertrepr_compare，这个函数会在测试脚本的assert语句执行时被调用。因此，可以实现这个函数，在函数中添加写日志和集成allure测试报告代码。
    '''
    left_name, right_name = inspect.stack()[7].code_context[0].lstrip().lstrip('assert').rstrip('\n').split(op)
    pytest_output = assertrepr_compare(config, op, left, right)
    # logging.debug("{0} is\n {1}".format(left_name, left))
    # logging.debug("{0} is\n {1}".format(right_name, right))
    with allure.step("校验结果"):
        allure.attach(str(left), left_name)
        allure.attach(str(right), right_name)
    return pytest_output



