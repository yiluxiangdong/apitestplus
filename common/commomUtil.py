# -*- encoding:utf-8 -*-
# D:\soft\pycharm\project\sunwoda\common\commomUtil.py
import copy
import getpass
import  uuid
import re
import socket
import sys
from json import load
from urllib.request import urlopen
import platform
import pandas as pd
from collections import defaultdict
#from common.commomUtil import read, write
import requests
#from redisUtil import RedisUtil
from common.redisUtil import RedisUtil
import glob
import json
import uuid
from itertools import chain
import random
import pandas as pd
import yaml
import os
import calendar
import time
import functools
from collections import defaultdict
from yaml import safe_load
from jinja2 import Template
from time import strftime
from datetime import date, timedelta, datetime
from yamlinclude import YamlIncludeConstructor
from jsonpath import jsonpath
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
logger = logging.getLogger(__name__)

import random

def forecastDate():
    dd = {}
    for j in range(12):
        dd.update({f"month{j + 1}": random.randint(1, 100) * 100})
    return dd

def forecast():
    dds = []
    for i in range(2):
        cc = forecastDate()
        cc.update({"forecastType": i})
        dds.append(cc)
    return dds

def mailbody(data):
    result = ''
    for item in sorted(data, key=lambda x: x['consumetime'],reverse=True):
        if item["status"]:
            color = {"status":'通过',"color":'green'}
        else:
            color = {"status": '失败', "color": 'red'}
        result = result + (
            f'<tr><td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["project"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["module"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["function"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["interface"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["api"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;color: {color["color"]};" >{color["status"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["consumetime"]}</td>'
            f'<td style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;" >{item["createtime"]}</td></tr>')
    return result

def send(projectname,result ,cnf=None):
    """
    import win32com
    print(win32com.__gen_path__)
    """
    data = [i for i in calctresult(result) if i['project'] == projectname][0]

    logger.info(f'发送测试结果邮件')
    sys_platform = platform.platform().lower()
    Subject = f"{projectname}接口自动化测试报告"

    # count = [list(account.values())[0]['mail_account'] for account in (cnf['project']['system']) if (list(account.values())[0]['name']) == projectname][0]
    count = [v["mail_account"] for _, v in (cnf['project']['system']).items() if v["name"] == projectname][0]
    Recipient = count['reception']
    From =count['send']
    item = mailbody(result)

    if str(data['passrate']) != '100.00%':
        color = 'red'
    else:
        color = 'green'

    # msg = f"{data['project']}累计运行用列数：{data['total']}条，其中成功{data.get('success', 0)}条，失败{data.get('fail', 0)}条，通过率{data.get('passrate', 0)},其中{data.get('modulepassrate', 0)}"
    htmlbody = f"""<body style="font-family: Arial, sans-serif; font-size: 12px ;">
                    <div><h5>各位领导、同事：<br>      
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; 收件好！</span><br>                   
                     关于{projectname}SIT环境接口自动化测试执行已于{strftime('%Y.%m.%d %H:%M:%S')}完成！</h5></div><br>
                    <h5 style="color: {color}; ">{data['msg']}</h5>
                    <table style="border-collapse: collapse;">
                      <tr>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">项目名称</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">模块名称</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">功能菜单</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">接口名称</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">接口路径</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">执行结果</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">接口耗时</th>
                        <th style="border: 1px solid black; padding: 4px;font-family: Arial, sans-serif; font-size: 10px ;">执行时间</th>
                      </tr>
                     {item}
                    </table>
                    <h3>详情请见附件！！！</h3><br>
                    <h5>[ ]企业绝密      [ ]企业机密       [✓]内部公开     [ ]外部公开<br>
                    **********************************************************<br>
                    欣旺达电子股份有限公司<br>
                    Sunwoda Electronic Co., Ltd.<br>
                    手机(Mobile)：181 6570 6145<br>
                    邮箱(E-mail):  liuxiaobing@sunwoda.com<br>
                    网址(Web)： http://www.sunwoda.com<br>
                    深圳市宝安区石岩街道石龙社区颐和路2号<br>
                    No.2, Yihe Rd, Shilong Community, Shiyan Street, Baoan District, Shenzhen, Guangdong, China<br>

                    声明：本邮件包含信息归发件人及发件人所在组织所有。请接收者注意保密，未经发件人书面许可，不得向任何第三方组织和个人透露本邮件所含信息的全部或部分。如果您错收本邮件，请您立即电话或邮件通知发件人并删除本邮件。<br>
                    Declaration: The information contained in this email belongs to the sender and their organization. Please keep the recipient confidential and not disclose all or part of the information contained in this email to any third party organization or individual without the written permission of the sender. If you received this email in error, please notify the sender immediately by phone or email and delete this email.lease notify the originator of the message</h5>

                    </body>
                    <p>
                    """
    try:
        if "windows" in sys_platform:
            import win32com.client as win32
            outlook = win32.Dispatch("outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = Recipient
            mail.CC = From
            mail.Subject = Subject
            mail.BodyFormat = 2
            mail.Attachments.Add(os.path.abspath('report/report.html'))
            mail.HTMLBody = htmlbody
            try:
                mail.Display(False)  # 显示发送邮件界面
                mail.Send()  # 发送
            except Exception as e:
                raise e
        else:
            os.system(
                f"echo '{htmlbody}' | mailx -s '{Subject}' -a {os.path.abspath('report/report.html')}  {Recipient.replace(';',',')}"
            )
    except Exception as e:
        raise e


def sendinfo(url,account,content):
    # 配置企业微信API的URL和Token
    # 构造消息体
    #"url" : f"http://192.168.12.79:5050/report/{content['keyId']}/{content['project']}",
    #"url" : f"http://127.0.0.1:5070/reportmysql/{content['keyId']}/{content['project']}",
    #mysql reportmysql  redis report
    msg = {
        "touser" : account,
        "toall" : 0,
        "msgtype" : "news",
        "agentid" : 1000012,
        "news" : {
           "articles" : [
               {
                   "title" : "自动化测试结果",
                   "description" : f"{content['project']}累计运行用列数：{content['total']}条，其中成功{content.get('success',0)}条，失败{content.get('fail',0)}条，通过率{content.get('passrate',0)}。<a >\n详情查看。</a>",
                   "url" : f"http://apitest.sunwoda.com:5070/report/{content['keyId']}/{content['project']}",
                   "picurl" : "https://crm-sit.sunwoda.com/file/crm/code/20241/2def68a649efe0a0b91edab9714bc569.png",
                   "btntxt":"更多"
               }
            ]
       }
    }

    return requests.post(url, json=msg).json()


def run(session, datas, url, content, logger, resultlist, index,sleeptime,loop):
    ''''
    执行用例部分
    '''
    body = datas.get("body")
    # if isinstance(body,str):
    #     body = json.loads(body)

    if sleeptime > 0:
        time.sleep(sleeptime)
        logger.error("\033[0;31m" + f'异步接口休眠时间：{sleeptime}' + "\033[0m")
    time.sleep(sleeptime)
    result = getattr(HTTP(logger), str(datas.get('method')).lower())(session, url=url, data=body)
    messagelist = [
        f'请求场景：第{index}次-->{datas.get("interfaceName")}',
        f'请求地址：{url}',
        f'请求参数：{json.dumps(datas.get("body"), ensure_ascii=False)}',
        # f'请求参数：{json.dumps(datas.get("body"), ensure_ascii=False, indent=2)}',
        f'预期结果：{datas.get("asserts")}',
        f'实际结果：{json.dumps(result.get("data"), ensure_ascii=False)}',
        # f'实际结果：{json.dumps(result.get("data"), ensure_ascii=False, indent=2)}',
        f'接口耗时：{result.get("consume")}']
    for info in messagelist:
        logger.info(info)
    if result.get('resultstatus'):
        if datas.get('save_key'):
            saveTempVal(datas, result.get('data'))  # 保存临时变量

    # 用例只要有一项不匹配就是不成功则返回False 成功则不返回
    assertsresult = asserts_test_result(result.get("data"), datas.get('asserts'))

    if assertsresult :
        resultstatus = True
    else:
        resultstatus = False
        logger.error("\033[0;31m" + f'接口异常,模块名称：{content[0]}，接口名称：{datas.get("interfaceName")}' + "\033[0m")
    resultlist.append(add_result(datas, result, resultstatus, index,loop))
    logger.info(f'获取断言结果')
    return resultstatus

def console_log(func):
    functools.wraps(func)
    logger = logging.getLogger(__name__)
    def inner(*args, **kwargs):
        funcname = func.__name__
        logger.info(f'执行{funcname}函数')
        res = func(*args, **kwargs)
        logger.info(f'函数{funcname}执行结果：{res}')
        return res
    return inner


@console_log
def init_time_args() -> dict:
    # 昨天日期date_yesterday
    timeformat = '%Y-%m-%d %H:%M:%S'
    dateformat = '%Y-%m-%d'
    date_yesterday = date.today() - timedelta(days=1)
    # 今天日期date_today
    date_today = date.today()
    time_today = strftime(timeformat)
    # 今天是几号
    datatoday = str(date.today()).split('-')[-1]

    # 明天日期date_tomorrow
    date_tomorrow = date.today() - timedelta(days=-1)

    # 昨天时间戳
    yesterday_timestamp = time.mktime(time.strptime(date_yesterday.strftime(dateformat), dateformat))
    # 今天时间戳
    current_timestamp = time.mktime(time.strptime(date_today.strftime(dateformat), dateformat))
    # 明天时间戳
    tomorrow_timestamp = time.mktime(time.strptime(date_tomorrow.strftime(dateformat), dateformat))

    # 上月初日期begin_data_last_month
    begin_data_last_month = datetime((datetime.now().replace(day=1) + timedelta(days=-1)).year,
                                     (datetime.now().replace(day=1) + timedelta(days=-1)).month, 1).strftime(dateformat)
    # 上月末日期end_data_last_month
    end_data_last_month = (datetime.now().replace(day=1) + timedelta(days=-1)).strftime(dateformat)
    # 本月初日期begin_data_current_month
    begin_data_current_month = datetime.now().replace(day=1).strftime(dateformat)
    # 本月末日期end_data_current_month
    a, b = calendar.monthrange(datetime.now().year, datetime.now().month)
    end_data_current_month = datetime(year=datetime.now().year, month=datetime.now().month, day=b).strftime(dateformat)
    # 下月初日期begin_data_next_month
    _, day = calendar.monthrange(date.today().year, date.today().month)
    begin_data_next_month = date.today() + timedelta(day - date.today().day + 1)
    # 下月末日期end_data_next_month
    _, day = calendar.monthrange(begin_data_next_month.year, begin_data_next_month.month)
    end_data_next_month = date(begin_data_next_month.year, begin_data_next_month.month, day)
    # 上月last_month
    last_month = (datetime.now().replace(day=1) + timedelta(days=-1)).strftime('%m')
    # 本月current_month
    current_month = datetime.now().replace(day=1).strftime('%m')
    # 下月next_month
    _, day = calendar.monthrange(date.today().year, date.today().month)
    next_month = (date.today() + timedelta(day - date.today().day + 1)).strftime('%m')
    # 去年last_year
    last_year = (datetime((datetime.now().replace(month=1, day=1) + timedelta(days=-1)).year, 1, 1)).strftime('%Y')
    # 今年current_year
    current_year = (datetime.now().replace(month=12, day=31)).strftime('%Y')
    # 明天next_year
    next_year = date.today().year + 1
    # 本周初日期
    begin_crrent_weekday = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime(dateformat)
    # 本周末日期
    end_crrent_weekday = (datetime.now() + timedelta(days=6 - datetime.now().weekday())).strftime(dateformat)
    # 上周初日期
    begin_last_weekday = (datetime.now() - timedelta(days=datetime.now().weekday() + 7)).strftime(dateformat)
    # 上周末日期
    end_last_weekday = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).strftime(dateformat)
    # 年初日期
    begin_data_current_year = (datetime.now().replace(month=1, day=1)).strftime(dateformat)
    # 年末日期
    end_data_current_year = (datetime.now().replace(month=12, day=31)).strftime(dateformat)
    # 去年初日期
    begin_data_last_year = (
        datetime((datetime.now().replace(month=1, day=1) + timedelta(days=-1)).year, 1, 1)).strftime(dateformat)
    # 去年末日期
    end_data_last_year = (datetime.now().replace(month=1, day=1) + timedelta(days=-1)).strftime(dateformat)
    datadict = {
        "date_yesterday": f"{date_yesterday}",
        "date_today": f"{date_today}",
        "time_today": f"{time_today}",
        "date_tomorrow": f"{date_tomorrow}",
        "yesterday_timestamp": f"{int(yesterday_timestamp)}",
        "current_timestamp": f"{int(current_timestamp)}",
        "tomorrow_timestamp": f"{int(tomorrow_timestamp)}",
        "begin_data_last_month": f"{begin_data_last_month}",
        "end_data_last_month": f"{end_data_last_month}",
        "begin_data_current_month": f"{begin_data_current_month}",
        "end_data_current_month": f"{end_data_current_month}",
        "begin_data_next_month": f"{begin_data_next_month}",
        "end_data_next_month": f"{end_data_next_month}",
        "last_month": f"{last_month}",
        "current_month": f"{current_month}",
        "next_month": f"{next_month}",
        "last_year": f"{last_year}",
        "current_year": f"{current_year}",
        "next_year": f"{next_year}",
        "begin_crrent_weekday": f"{begin_crrent_weekday}",
        "end_crrent_weekday": f"{end_crrent_weekday}",
        "begin_last_weekday": f"{begin_last_weekday}",
        "end_last_weekday": f"{end_last_weekday}",
        "begin_data_current_year": f"{begin_data_current_year}",
        "end_data_current_year": f"{end_data_current_year}",
        "begin_data_last_year": f"{begin_data_last_year}",
        "end_data_last_year": f"{end_data_last_year}",
        "randmun": f"{(str(uuid.uuid4()).split(('-'))[-1]).upper()}",
        "datetimename": datetime.now().strftime("%Y%m%d%H%M%S"),
        "datatoday": datatoday,
        "randintdata": str(random.randint(1, 99999)).rjust(5, '0')

    }
    return datadict


@console_log
def update_request_parameters(temp, data):
    logger.info(f'替换测试数据中的临时变量')
    return safe_load(Template(data).render(temp))

@console_log
def is_excel_yaml_file(file_path: str, types: list) -> bool:
    """
    判断文件是否为Excel文件。 ['.xls', '.xlsx'] ['.yaml']:
    :param file_path: 文件路径。
    :return: 如果文件是Excel文件则返回True，否则返回False。
    """
    return True if os.path.splitext(file_path)[1].lower() in types else False

@console_log
def deldate(data,key):
    del data[key]
    return data
@console_log
def readexcelcase(path,index):
    result = []
    for files in glob.glob(os.path.join(path, "*.xls*")):
        df = pd.read_excel(files, sheet_name=index)
        datas = df.to_dict('records')
        for item in datas:
            if item.get('body') or item.get('asserts'):
                item['body'] = json.loads(item['body'])  # 字符串转换成字典
                item['save_key'] = [i for i in item['save_key'].strip('[]').split(',')]  # 字符串转换成列表
                item['asserts'] = [i for i in item['asserts'].strip('[]').split(',')]  # 字符串转换成列表
                item.update({'path':files})
                result.append(item)
    if index == 1:
        d = defaultdict(list)
        [d[data['interfaceName']].append(deldate(data,'interfaceName')) for data in result]
        result = dict(d)
    return result


# @console_log
def readyamlcase(path,index=0):
    result = []
    if os.path.exists(path):
        if index == 0:
            for files in glob.glob(os.path.join(f"{path}", '*.yaml')):
                if 'params.yaml' not in files:
                    data = read(files)
                    if data:
                        for items in read(files):
                            if isinstance(items, dict):
                                items.update({'path':files})
                                result.append(items)
        else: # 替换的参数
            result = read(os.path.join(f"{path}", 'params.yaml'))
    else:
        result = []
    return result

@console_log
def readAllcase(path, readexcel, index=None):
    if readexcel == True:
        result = readexcelcase(path,index)
    elif readexcel == False:
        result = readyamlcase(path, index)
    else:
         #读取所有用例
         if index ==0:
             result = readexcelcase(path,0)+readyamlcase(path, 0)
             #记录用例所在文件地址
             d = defaultdict(list)
             [d[item['path'].split('\\')[-1]].append(item['interfaceName'])for item in result]
             logger.info(f'记录用例所在文件地址:{dict(d)}')
             write((r'./config/casepath.yaml'),dict(d))
         else:
             result = readexcelcase(path, 1)
             param = readyamlcase(path, 1)
             if param:
                result.update(readyamlcase(path, 1))
    return result

@console_log
def read(path: str) -> dict:
    """
    读取文件
    """
    logger.info(f'读取{path}文件数据')
    YamlIncludeConstructor.add_to_loader_class(loader_class=yaml.FullLoader)
    if is_excel_yaml_file(path, ['.yaml']):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                # return yaml.load(f, Loader=yaml.FullLoader)
                return yaml.unsafe_load(f)
        except:
            with open(path, 'w', encoding='utf-8', errors='ignore') as f:
                return None

@console_log
def write(path: str, data):
    """
    写入文件
    """
    with open(path, 'w', encoding='utf-8') as f:
        return yaml.dump(data, f, allow_unicode=True, sort_keys=False)
@console_log
def cleanfile(path: str, ):
    """
    写入文件
    """
    with open(path, 'w') as file:
        file.truncate()

@console_log
def updatefile(path: str, newdata):
    """
    写入文件
    """
    data = read(path)
    data.update(newdata)
    write(path,data)


@console_log
def Splitstring(strings):
    blist = []
    if '==' in strings:
        olderStr = strings.split('=')
        for i in range(len(olderStr)):
            if olderStr[i] == '':
                if olderStr[i - 1] not in blist:
                    blist.append(olderStr[i - 1])
                if olderStr[i + 1] not in blist:
                    blist.append(olderStr[i + 1])
        result = ''
        for i in blist:
            result = result + i + '=='
        return [result.strip('=='), olderStr[-1]]
    else:
        return strings.split('=')

@console_log
def get_request_parameters(base_conf) -> list:
    logger.info('从文件中读取测试用例数据')
    path = base_conf['case_path']['dir_name']
    temp = readAllcase(path, base_conf['byexcel']['enable'], 0)
    logger.info(f'从文件中读取测试用例数据{temp}')  #从文件中读取的测试用例
    #1.将测试数据按照所属系统分类
    templist = defaultdict(list)
    for detail in temp:
        templist[detail['interfaceName'].split("_")[0]].append(detail)
    # 2.根据配置将需要执行的用例筛选出来(需要base文件哪个系统是否执行)
    case_list = list(chain(*[v for k,v in dict(templist).items() if jsonpath(base_conf, f'$..[?(@.name == "{k}")].enable')[0] ]))
    #3.读取casename文件中配置的需要执行的用例
    case_conf = read(r'./config/casename.yaml')
    if base_conf["runallcase"]["enable"] or not case_conf:
        #1.如果casename文件为空就是默认之前符合要求的用（只要满足第二部筛选出来的用例就可以）
        #2.将所执行的用例写入casename文件
        casename_file = defaultdict(list)
        for item in case_list:
            casename_file[item['interfaceName'].split("_")[0]].append(item['interfaceName'])
        if case_conf:
            cleanfile(r'./config/casename.yaml')
        write(r'./config/casename.yaml', dict(casename_file))
    else:
        #1.如果casename文件中配置的有需要执行的用例
        casename = list(chain(*[interfaceName for _, interfaceName in case_conf.items()]))  # 配置中的用例
        new_case_list = []
        for case in case_list:
            for index in range(len(casename)):
                if case['interfaceName'] == casename[index]:
                    new_case_list.insert(index, case)
        case_list = new_case_list

    return case_list

@console_log
def saveTempVal(req_data, resp_data):
    '''
    req_data yaml文件中的数据
    resp_data 返回的报文
    '''
    try:
        res = {}
        save_key = req_data.get("save_key")
        # if isinstance(save_key, str):
        #     save_key = save_key.lstrip("[").rstrip(']').split(",")
        for detail in save_key:
            item = Splitstring(detail)
            values = jsonpath(resp_data, item[0].strip())
            if item[1].strip().endswith("*"):
                data = {item[1].strip().rstrip("*"): values}
            else:
                data = {item[1].strip(): values[0]}
            logger.info(f'保存临时变量--->{data}')
            res.update(data if values else {item[1].strip(): None})
        # 更新写入temp文件
        logger.info(f'将临时文件写入temp中--->{res}')
        updateTemp(r'./config/temp.yaml', res)
        # r = redisdb()
        # if r:
        #     r.savedict('temp',res,'更新临时变量到缓存中')
        return res
    except Exception as e:
        return e


# @console_log
def updateTemp(path: str, data):
    '''
    req_data yaml文件中的数据
    resp_data 返回的报文  r'./config/temp.yaml'
    '''
    logger.info(f'更新临时变量{data}')
    data.update(read(path))
    cleanfile(path)
    write(path, data)



def isvaild_case(base_cnf, data) -> bool:
    caseconf = base_cnf["case_config"]["key"]
    case_key_list = [k for k, _ in data.items()]
    if set(case_key_list) > set(caseconf["requiredkey"]):
        logger.info("测试用例符合规范")
        return True
    else:
        logger.info("测试用例不符合规范")



def add_result(datas, result=None, status=None, index=None, loop=None) -> dict:
    interfaceName = datas.get("interfaceName")
    consumetime = round(result.get("consume"), 2) if isinstance(result, dict) else 0
    message = 'run success' if status else 'run fail'
    resresult = {
        "name": interfaceName + f'_{index}' if loop > 1 else interfaceName,
        "project": interfaceName.split("_")[0],
        "module": interfaceName.split("_")[1],
        "function": datas.get("function"),
        "interface": interfaceName,
        "message": message,
        "status": status,
        "api": datas.get("url"),
        'consumetime': consumetime,
        "createtime": strftime("%Y-%m-%d %H:%M:%S"),
        "result": json.dumps(result.get('data', None), ensure_ascii=False)
    }
    resresult.update(computer_information())
    return resresult

def computer_information() -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    currentIp = s.getsockname()[0]
    try:
        publicIp = load(urlopen('http://httpbin.org/ip'))['origin']
    except:
        publicIp = '0.0.0.0'

    return {
        "currentIp": currentIp,
        "publicIp": publicIp,
        "UserName": getpass.getuser(),
        "hostName": socket.gethostname(),
    }

def replace_none(test_dict):
    if isinstance(test_dict, dict):
        for key in test_dict:
            if test_dict[key] == "None" or test_dict[key] == None:
                test_dict[key] = None
            else:
                replace_none(test_dict[key])

    elif isinstance(test_dict, list):
        for val in test_dict:
            replace_none(val)


def replacedata(data):
    b = copy.deepcopy(data)
    replace_none(b)
    return b

def asserts_test_result(response=None, asserts=None) -> bool:
    assertlist = []
    import re
    # if isinstance(asserts,str):
    #     asserts = [i.strip("'") for i in (asserts.strip("'[").strip("]'").split(","))]
    for items in asserts:
        date = re.split('==|\!=', items)
        result = jsonpath(response, date[0].strip())
        asserttxt = date[1].strip()
        if result:
            if "==" in items:
                if str(result[0]) == asserttxt:
                    assertlist.append(True)
                else:
                    assertlist.append(False)
            elif "!=" in items:
                if result[0] != "":
                    assertlist.append(True)
                else:
                    assertlist.append(False)
        else:
            assertlist.append(False)
    if False in assertlist:
        return False
    else:
        return True

def  calctresult(data= None):
    keyId = read(r'./config/temp.yaml')['datetimelist']['datetimename']
    resultlist = []
    d = defaultdict(list)
    [d[item['project']].append(item) for item in data]
    for k, v in (dict(d)).items():
        total = len(v)
        success = len([i for i in v if i['status'] == True])
        fail = total-success
        #计算系统整体通过率
        passrate = '{:.2%}'.format(success / total)
        #计算每个模块通过率
        d1 = defaultdict(list)
        [d1[i['module']].append(i) for i in v]
        module = [f"{k}模块通过率{'{:.2%},'.format(sum(item['status'] for item in v) / len(v))}" for k, v in  dict(d1).items()]
        strings = ''
        for i in module:
            strings = strings + i
        modulepasrate = strings.strip(',')
        resultlist.append({'project':k,
                           'keyId': keyId,
                           "total": total,
                           "success": success,
                           "fail": fail,
                           'passrate':passrate,
                           'modulepassrate': modulepasrate,
                           'msg':f"{k}累计运行用列数：{total}条，其中成功{success}条，失败{fail}条，通过率{passrate},其中{modulepasrate}"
                           })
    return resultlist

def getresultbyredis(keyId,project):
    conf = read(r'../config/base.yaml')['db_redis']
    r = RedisUtil(conf['host'], conf['port'], conf['password'])
    detailllist = []
    for detail in r.getdata("errorlist"):
        items = json.loads(detail)
        if items['keyId'] == keyId and items['project'] == project:
            detailllist.append(items)
    d = {}
    for item in (detailllist):
        d['result'] = json.loads(item["result"])
        d['data'] = [j for j in json.loads(item['detaill'])]
    return d

def readdate(filename):
    if is_excel_yaml_file(filename, ['.yaml']):
        data = read(filename)
    else:
        data = []
        # 使用 pd.ExcelFile 读取文件但不加载数据
        excel_file = pd.ExcelFile(filename)
        # 获取所有 sheet 名称
        sheet_names = excel_file.sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(filename, sheet_name=sheet)
            datas = df.to_dict('records')
            for item in datas:
                if item.get("body") or item.get("asserts"):
                    item['body'] = json.loads(item['body'])  # 字符串转换成字典
                    item['save_key'] = [i for i in item['save_key'].strip('[]').split(',')]  # 字符串转换成列表
                    item['asserts'] = [i for i in item['asserts'].strip('[]').split(',')]  # 字符串转换成列表
            data.append({'sheet_names': sheet, 'data': datas})

    try:
        # return  json.dumps(data,indent=2,ensure_ascii=False)
        return data
    except:
        return None


def timestamps(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def getfilesize(file):
    filesize = os.path.getsize(file)
    file_bytes = filesize / (1024 * 1024)
    if file_bytes > 1:
        return f'{round(file_bytes, 2)}M'
    elif filesize > 1024:
        return f'{round(filesize / 1024, 2)}kb'
    else:
        return f'{filesize}b'


def get_file_paths(directory,types):
    file_paths = []
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        content = ''
        filetype = ''
        filename = ''
        filesize = ''
        createTime = ''
        lastaccesstime = ''
        lastupdatetime = ''
        if os.path.isfile(file_path):
            file_stats = os.stat(file_path)
            filename = re.split(r'[\\/]', file_path)[-1]
            filesize = getfilesize(file_path)
            # createTime = datetime.fromtimestamp(os.path.getctime(file_path)).date().strftime('%Y-%m-%d')
            createTime = timestamps(file_stats.st_ctime)
            lastaccesstime = timestamps(file_stats.st_atime)
            lastupdatetime = timestamps(file_stats.st_mtime)
            if file.endswith('.yaml') or file.endswith('.xlsx') or file.endswith('.xls') :
                if filename not in ['template.yaml','template.xlsx']:
                    content = readdate(file_path)
                    filetype = 'casefile'
            else:
                filetype = 'no_casefile'
        file_paths.append({
            "filepath": file_path,
            "filename": filename,
            "filesize": filesize,
            'filetype':filetype,
            "createTime": createTime,
            'lastaccesstime':lastaccesstime,
            'lastupdatetime':lastupdatetime,
            "content": content
        })

    from collections import defaultdict
    d = defaultdict(list)
    for file in file_paths:
        index = file_paths.index(file)
        file['index'] = index + 1
        d[file['filetype']].append(file)
    return dict(d).get('casefile',[]) if types else  dict(d).get('no_casefile',[])

class HTTP:
    TIMEOUT = 5
    data = ''
    try:
        data = read(r'./config/base.yaml')
    except:
        data = read(r'../config/base.yaml')
    # proxies =data['proxies'] if sys.platform.startswith('linux') else None
    #proxies =data['proxies'] if sys.platform.startswith('linux') else None
    proxies ={'http': 'http://172.30.7.125:3128'} if sys.platform.startswith('linux') else None
    def __init__(self, logger):
        self.logger = logger

    def httpmode(self, request=None, sessions=None, url=None, data=None):
        self.logger.info(f'发送http请求返回结果')
        try:
            result = eval(request)
            res = result.json()
            res.update({'status': result.status_code})
            return {
                'data': res,
                "consume": result.elapsed.total_seconds(),
                'resultstatus': True
            }

        except requests.exceptions.RequestException as e:
            return {
                'data': {'message': f'请求超时,{e}', 'status': 504},
                "consume": round(random.uniform(self.TIMEOUT, self.TIMEOUT + 10), 2),
                'resultstatus': False
            }
        except:
            return {
                'data': {'message': f'请求异常,Remote end closed connection without response', 'status': 504},
                "consume": round(random.uniform(self.TIMEOUT, self.TIMEOUT + 10), 2),
                'resultstatus': False
            }

    def post(self, sessions, url=None, data=None):
        return self.httpmode(
            f'sessions.post(url=url, json=data, verify=False,proxies = {self.proxies},  timeout={self.TIMEOUT})',
            sessions, url,
            data)

    def put(self, sessions, url=None, data=None):
        return self.httpmode(
            f'sessions.put(url=url, json=data, verify=False,proxies = {self.proxies}, timeout={self.TIMEOUT})',
            sessions, url,
            data)

    def get(self, sessions, url=None, data=None) -> dict:
        return self.httpmode(
            f'sessions.get(url=url, params=data, verify=False,proxies = {self.proxies},  timeout={self.TIMEOUT})',
            sessions, url,
            data)

    def param(self, sessions, url=None, data=None) -> dict:
        return self.httpmode(
            f'sessions.post(url=url, params=data, verify=False,proxies = {self.proxies},  timeout={self.TIMEOUT})',
            sessions,
            url, data)

    def formdata(self, sessions, url=None, data=None) -> dict:
        '''
        formdata参数
        上传文件  D:\autoTest\sunwoda\files\合同测试模板.docx
        '''
        return self.httpmode('sessions.post(url=url, params=data, files={"file": open("./files/合同测试模板.docx", "rb")}, '
                             f'verify=False,proxies = {self.proxies},  timeout={self.TIMEOUT})', sessions, url, data)

    def formpng(self, sessions, url=None, data=None) -> dict:
        '''
        formdata参数
        上传文件  ./files/封面1211.png
        D:/Users/2204010095/Desktop/上传文件/回款测试.png
        headers = {"Content-Type":"multipart/form-data"}
        '''
        return self.httpmode('sessions.post(url=url, params=data, files={"file": open("./files/封面1211.jpeg", "rb")}, '
                             f'verify=False,proxies = {self.proxies},  timeout={self.TIMEOUT})', sessions, url, data)

def getmkcookie():
    '''
    获取mk的cookies
    '''
    conf = read(r'../config/base.yaml')['mk']
    # 设置无头模式（无图模式）
    options = Options()
    options.add_argument("--headless")
    # 初始化WebDriver
    driver = webdriver.Chrome(options=options)
    # 打开登录页面
    driver.get(conf["host"])
    driver.implicitly_wait(10)

    # 假设用户名和密码已经预先处理好，直接输入
    driver.find_element(By.ID, "username").send_keys(conf["account"][0]["user"]["username"])
    driver.find_element(By.ID, "password").send_keys(conf["account"][0]["user"]["password"])
    # 提交登录信息（如果需要）
    driver.find_element(By.TAG_NAME, "button").click()
    # 等待页面加载完成
    time.sleep(3)
    # 获取cookie
    cookies = driver.get_cookies()
    # 打印cookie信息
    cookies_str = ""
    for cookie in cookies:
        cookies_str += f"{cookie['name']}={cookie['value']};"
    # 关闭浏览器
    driver.quit()
    return cookies_str + "Hm_lvt_64a5fcc99251736c1796413cb4e20e10=1712022157"


def getmkcookies(username,password):
    '''
    获取mk的cookies
    '''
    conf = read(r'../config/base.yaml')['mk']
    # 设置无头模式（无图模式）
    #options = Options()
    #options.add_argument("--headless")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # 初始化WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    # 打开登录页面
    driver.get(conf["host"])
    driver.implicitly_wait(10)

    # 假设用户名和密码已经预先处理好，直接输入
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    # 提交登录信息（如果需要）
    driver.find_element(By.TAG_NAME, "button").click()
    # 等待页面加载完成
    time.sleep(3)
    # 获取cookie
    cookies = driver.get_cookies()
    # 打印cookie信息
    cookies_str = ""
    for cookie in cookies:
        cookies_str += f"{cookie['name']}={cookie['value']};"
    # 关闭浏览器
    driver.quit()
    return cookies_str + "Hm_lvt_64a5fcc99251736c1796413cb4e20e10=1712022157"

def selectcaseitem(projectName):
    path = r'../databak'
    result = []
    d=defaultdict(list)
    for case in (readexcelcase(path, 0)+ readyamlcase(path, 0)):
        if str(projectName).split("-")[0].upper() in case['interfaceName']:
            result.append({case['interfaceName'].split("_")[0]:case['interfaceName']})
    [d[list(i.keys())[0]].append(list(i.values())[0]) for i in result]
    # write((r'../config/casename.yaml'),dict(d))
    data = dict(d)
    for k, casename in read(r'../config/casename.yaml').items():
        if str(projectName).split("-")[0].upper() in k:
            data['checkedcase'] = casename
    return data

    # return dict(d)
######################################################################################

def  getfileinfo(directory):
    file_paths = []
    content = ''
    for file in os.listdir(directory):
        file_path = os.path.join(directory, file)
        file_stats = os.stat(file_path)
        filename = re.split(r'[\\/]', file_path)[-1]
        if file.endswith('.yaml') or file.endswith('.xlsx') or file.endswith('.xls'):
            if filename not in ['template.yaml', 'template.xlsx']:
                if '备份' not in filename:
                    content = readdate(file_path)
                    filetype = 'testfile' #测试文件
                else:
                    filetype = 'backfile'  # 测试文件
            else:
                filetype = 'tempfile'  # 测试文件

        elif  file.endswith('.jmx'):
            filetype = 'stress_testfile' #压力测试文件
        else:
            if '备份' not in filename:
                filetype = 'no_testfile'  # 非测试文件
            else:
                filetype = 'backfile'  # 测试文件
        file_paths.append({
            "filepath": file_path,
            "filename": re.split(r'[\\/]', file_path)[-1],
            "filesize": getfilesize(file_path),
            'filetype': filetype,
            "createTime": timestamps(file_stats.st_ctime),
            'lastaccesstime': timestamps(file_stats.st_atime),
            'lastupdatetime': timestamps(file_stats.st_mtime),
            "content": content
        })
    return file_paths


def  getloginfo(file_paths):
    # file_paths = r'E:\sunwoda\reportserver\run.log'
    file_stats = os.stat(file_paths)
    filetype = 'logfile'
    with open(file_paths, 'r', encoding='utf-8') as f:
        content = f.read()
    file_info = {
        "filepath": file_paths,
        "filename": re.split(r'[\\/]', file_paths)[-1],
        "filesize": getfilesize(file_paths),
        'filetype': filetype,
        "createTime": timestamps(file_stats.st_ctime),
        'lastaccesstime': timestamps(file_stats.st_atime),
        'lastupdatetime': timestamps(file_stats.st_mtime),
        "content": content
    }
    return file_info
 
def getnewconf(old_conf, file_path, index=0):
    df = pd.read_excel(file_path, skiprows=1, sheet_name=index)
    df = df.fillna("")
    datas = df.to_dict('records')
    accountlist = []
    for i in datas:
        if i.get('header'):
            if i['role']:
                accountlist.append({
                        "project" : i['project'],
                        'account' : {
                            i['role'] : {
                                'username' : i['username'],
                                'password' : i['password'],
                                'header' : json.loads(i['header'])
                            }
                        }
                    })
            else:
                accountlist.append({
                    "project" : i['project'],
                    'account' : {
                        'username' : i['username'],
                        'password' : i['password'],
                        'header' : json.loads(i['header'])
                    }
                })
        else:
            if i['role']:
                accountlist.append({
                    "project": i['project'],
                    'account': {
                        i['role']: {
                            'username': i['username'],
                            'password': i['password'],
                            'header': i['header']
                        }
                    }
                })
            else:
                accountlist.append({
                    "project": i['project'],
                    'account': {
                        'username': i['username'],
                        'password': i['password'],
                        'header': i['header']
                    }
                })
        del i['username']
        del i['password']
        
    d = defaultdict(list)
    for i in accountlist:
        d[i['project']].append(i['account'])

    oldconf = read(old_conf)
    newconf = [{k: {"account": v}} for k, v in (dict(d)).items()]
    for kk in newconf:
        if list(kk.keys())[0] in oldconf:
            if isinstance(oldconf[list(kk.keys())[0]]['account'], list):
                oldconf[list(kk.keys())[0]]['account'] = merge_lists(oldconf[list(kk.keys())[0]]['account'],
                                                                     list(kk.values())[0]['account'])
            else:
                oldconf[list(kk.keys())[0]]['account'].update(kk[list(kk.keys())[0]]['account'][0])
    write(old_conf, oldconf)
    # return oldconf


def merge_configs(old, new):
    merged = {}

    # Convert old list to dictionary
    for item in old:
        if isinstance(item, dict):
            for k, v in item.items():
                if isinstance(v, dict):
                    merged[k] = v

    # Merge new list into the dictionary
    for item in new:
        if isinstance(item, dict):
            for k, v in item.items():
                if k in merged:
                    if isinstance(merged[k], dict) and isinstance(v, dict):
                        merged[k].update(v)
                else:
                    merged[k] = v

    # Convert back to list of dictionaries
    return [{k: v} for k, v in merged.items()]

def merge_lists(aa, bb):
    merged_dict = {list(item.keys())[0]: item for item in aa if isinstance(item, dict)}

    for item in bb:
        if isinstance(item, dict):
            key = list(item.keys())[0]
            if key in merged_dict:
                if isinstance(merged_dict[key][key], dict) and isinstance(item[key], dict):
                    merged_dict[key][key].update(item[key])
            else:
                merged_dict[key] = item

    return list(merged_dict.values())

import  uuid
def rundomNum(munber,count):
    char_map = {
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
        'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15,
        'A': 16, 'B': 17, 'C': 18, 'D': 19, 'E': 20, 'F': 21,
        '-': 22  # UUID中的短横线
    }

    digit_list = [char_map[char] for char in str(uuid.uuid4())]
    digit_str = ''.join(map(str, digit_list))
    return [digit_str[0:int(munber)] for i in range(int(count))]

if __name__ == "__main__":
    print(rundomNum(6))
   