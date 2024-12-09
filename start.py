# -*- encoding:utf-8 -*-
# E:\sunwoda\start.py
import json
import os
import shutil
from collections import defaultdict
import platform
from datetime import datetime


import pytest
import yaml
import logging

logger = logging.getLogger(__name__)
# import easygui
from common.commomUtil import read, init_time_args, write,send
from conftest import base_cnf,Redis

# """
# cmd:#计算耗时
# python -m cProfile -s cumulat  TEST_order_pro.py conftest.py
# 1.导出当前安装的包记录:pip freeze >  requirements.txt
# 2.导入安装之前的包列表:pip install -r  requirements.txt
# 3.升级pip python -m pip install --upgrade pip
# 4.print('写入日志', file = open('log.log','w'))
# D:/Python/Lib/pathlib.py   def write_text(self, data, encoding='utf-8', errors=None)修改了代码
# pip freeze > requirements.txt      导出依赖包信息至requirements.txt文件
# pip install -r requirements.txt    安装依赖
# allure open -h 127.0.0.1 -p 8888 ./report/
#fatal error in launcher
# python -m pip install  --upgrade --force-reinstall pip
#升级 pip：运行命令python -m pip install --upgrade pip来将 pip 更新到最新版本。
#清除 pip 缓存：执行命令pip cache purge来清除 pip 缓存。
#Cache entry deserialization failed, entry ignored 错误解决  python -m pip install --upgrade pip
#Consider using the `--user` option or check the permissions.  python -m pip install pyqt5-tools  或者 --user
#ln -s   /usr/local/python3/Python-3.7.9/bin/python3.7  python3 
#ln -s    /usr/local/python3/Python-3.7.9/bin/pip3.7  pip3
#ln -s    /usr/local/python3/Python-3.13/bin/python3.13  python3 
#ln -s    /usr/local/python3/Python-3.13/bin/pip3.13  pip3
# """

def run():
    """
    每次运行之前删除日志和上次构建的测试报告
    """
    #指定文件名
    # 降临时变量持久化到文件
    write(r'./config/temp.yaml', {'datetimelist':init_time_args()})
    name = read(r'./config/temp.yaml')['datetimelist']['datetimename']
    result_dir = r"./report/result"
    report_dir = r"./report/report"
    reportfile = f"./report/report.html"
    temp_dir = r"./.pytest_cache"
    filelist = [result_dir, report_dir, reportfile, temp_dir]
    for item in filelist:
        if os.path.exists(item):
            shutil.rmtree(item) if os.path.isdir(item) else os.remove(item)
    pytest.main(["-sv", "--alluredir={}".format(result_dir), "--clean-alluredir", "--html={}".format(reportfile), "--capture=sys"])
    sys_platform = platform.platform().lower()

    #复制备份测试报告
    odlfile = f'./report/report.html'
    filename = f'./report/report{name}.html'
    shutil.copy(odlfile, filename)
    ret = ''
    if "windows" in sys_platform:
        try:
            os.system(fr'copy  environment.properties report\result /y')
            ret = os.system(f"allure generate --clean {result_dir} -o {report_dir}")
        except Exception as e:
            print(e)
    else:
        allure = '/usr/local/tools/allure-2.16.0/bin/allure'
        os.system(f'cp environment.properties {result_dir}')
        ret = os.system(f"{allure} generate --clean {result_dir} -o {report_dir}")

    '''
    所有运行项目发送文件配置全部都是True才发送邮件提示
    '''
    d = defaultdict(list)
    [d[item['project']].append(item) for item in read(r'./config/result.yaml')]
    for projectName, result in dict(d).items():
        if base_cnf['mail'].get("enable",False): #判断是否发送邮件
            print('发送{}测试结果邮件'.format(projectName))
            send(projectName,result, base_cnf)
        else:
            print('不发送邮件')
    if not ret:
        # if easygui.ynbox('是否展示测试报告'):
        #     os.system(f"allure open -h 127.0.0.1 -p 8888 {report_dir}")
        print('生成测试报告成功')
        # html2jpg()
    else:
        print('生成测试报告失败')

    errorlist = []
    for i in Redis.getdata('errorlist'):
        result = json.loads(i)
        if result['keyId'] == read(r'./config/temp.yaml')['datetimelist']['datetimename']:
            createtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            errorlist.append({"keyId": result['keyId'], "project": result['project'], "createtime": createtime,"detaill":result['detaill']})
    print(f'保存jenkins构建结果:{errorlist}')
    Redis.savedict('runresult',errorlist,'保存jenkins构建结果')
    logger.info('保存jenkins构建结果')
    # if "windows" not  in sys_platform:
    #     url = base_cnf['jenkins']['url']
    #     username = base_cnf['jenkins']['username']
    #     password = base_cnf['jenkins']['password']
    #     server = jenkins.Jenkins(url, username, str(password)) 
    #     server = jenkins.Jenkins(url, username, str(password)) 
    #     errorlist = []
    #     jobname = ''
    #     for i in Redis.getdata('errorlist'):
    #         result = json.loads(i)
    #         if result['keyId'] == read(r'./config/temp.yaml')['datetimelist']['datetimename']:
    #             if result['project'] == "会议系统":
    #                 jobname = 'Meet-API-test'
    #             elif result['project'] == "SRM系统":
    #                 jobname = 'SRM-API-test'
    #             elif result['project'] == "OTD系统":
    #                 jobname = 'OTD-API-test'
    #             elif result['project'] == "CRM系统":
    #                 jobname = 'CRM-API-test'
    #             number = server.get_job_info(jobname)['lastBuild']['number']
    #             errorlist.append({"keyId": result['keyId'], "jobname": jobname, "project": result['project'], "number": number,"detaill":result['detaill']})
    #     print(f'保存jenkins构建结果:{errorlist}')
    #     Redis.savedict('runresult',errorlist,'保存jenkins构建结果')
    #     logger.info('保存jenkins构建结果')


if __name__ == "__main__":
    run()


