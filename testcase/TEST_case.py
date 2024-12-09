# -*- encoding:utf-8 -*-
# D:\autoTest\sunwoda\testcase\TEST_case.py
import json
import random
from collections import defaultdict
import allure
import pytest
import logging
from datetime import datetime
from time import strftime
from dateutil.parser import parse
from common.commomUtil import sendinfo,update_request_parameters, write, cleanfile, read, readAllcase,add_result, isvaild_case, replacedata, logger, calctresult,run
from common.zendaoUtil import zendaodb
from common.dbUtil import apitest
from conftest import casedata, test_cnf, base_cnf, initdatas,Redis
from jsonpath import jsonpath


class Test_case:
    resultlist = []
    logger = logging.getLogger(__name__)
    case = casedata()
    #parmas = readAllcase(base_cnf['case_path']['dir_name'], base_cnf['byexcel']['enable'], 1)
    def setup_class(self):
        self.logger.info("\033[0;31m" + '如需执行所有用例请清空casename.yaml文件' + "\033[0m")
        self.logger.info('开始执行')
        self.logger.info(f'开始执行{self.case}')

    @pytest.mark.parametrize('data', case, ids=['测试：{}'.format(case['interfaceName']) for case in case])
    def test_model(self, sessions, data):
        if data:
            self.temp = read(r'./config/temp.yaml')
            datas = replacedata(update_request_parameters(self.temp, str(data)))
            if isvaild_case(base_cnf, datas):
                content = datas.get('interfaceName').split('_')
                allure.dynamic.feature(content[0])
                allure.dynamic.story(content[1])
                allure.dynamic.title(content[2])
                allure.dynamic.severity(datas.get('level'))
                self.logger.info(f'开始执行接口{datas.get("interfaceName")}{datas}')
                self.test_model.__func__.__doc__ = datas.get('interfaceName')
                conf = [v for _, v in test_cnf.items() if v['desc'] == content[0]][0]
                if conf:
                    if not isinstance(conf['account'], list):  # 如果配置文件没有role字段
                        roles = base_cnf['default'].get('role', '管理员')
                    else:
                        cnfrole = [list(i.keys())[0] for i in conf['account']]
                        roles = datas.get("role")
                        roles = roles if roles in cnfrole else False
                    if roles:  # 测试数据文件与配置文件角色对比
                        session = jsonpath(sessions, f'$.{content[0]}.{roles}')[0]
                        self.logger.info(f'获取{content[0]}系统平台{roles}的登录Cookies:{session}')
                        self.logger.info(f'获取系统平台的登录header:{session.headers}')
                        url = datas.get("url")
                        loop = datas.get("loop", 1)
                        self.logger.info(f'获取循环次数：{loop}')
                        host = conf['host']
                        if session:
                            url = url if host in url else host + url
                            sleeptime = int(datas.get('sleeptime', 0))
                            asserts = run(session, datas, url, content, self.logger, self.resultlist, 1, sleeptime, int(loop))
                            pytest.assume(asserts)
                        else:
                            message = '初始化数据中session不存在'
                            self.resultlist.append(add_result(datas, {"consume": None, "data": message}, False, message))
                            self.logger.error("\033[0;31m" + message + "\033[0m")
                            assert False
                    else:
                        message = '测试用例中role角色名称与配置文件config.yaml中的role名称不一致,或者缺失'
                        self.logger.error("\033[0;31m" + message + "\033[0m")
                        assert False
                else:
                    message = '测试用例中interfaceName的模块名称与配置文件config.yaml中名称不一致,或者vaild配置项为n'
                    self.resultlist.append(add_result(datas, {"consume": None, "data": message}, False, message))
                    self.logger.error("\033[0;31m" + message + "\033[0m")
                    assert False
            else:
                self.logger.error(
                    "\033[0;31m" + f"{datas.get('interfaceName')} ---->测试用例不符合规范,单个测试用例必须包含{base_cnf['case_config']['key']['requiredkey']}这些字段" + "\033[0m")
                assert False
        else:
            self.logger.error("\033[0;31m" + f"测试用例文件不存在，请确认配置文件是否正确" + "\033[0m")
            assert False

    def teardown_class(self):
        starttime = initdatas['starttime']
        endtime = strftime('%Y-%m-%d %H:%M:%S')
        total = (parse(endtime) - parse(starttime)).total_seconds()
        self.logger.info(f'打印测试结果：{self.resultlist}')
        self.logger.info(f'将测试结果写入文件中')
        cleanfile(r'./config/result.yaml')
        write(r'./config/result.yaml', self.resultlist)
        passrate = calctresult(self.resultlist)
        ############################调用禅道接口############################
        buglist = [i for i in self.resultlist if not i['status']]
        if base_cnf['zentao'].get("enable", False):
            try:
                for item in buglist:
                    logger.info(f'{item["api"]}接口报错，提交禅道bug')
                    zendaodb(base_cnf).createBUG(item['interface'], item)
            except Exception as e:
                logger.info(f'禅道系统异常：{e}')
        else:
            logger.info(f'禅道配置无需提交bug')
        ############################ 合并测试结果计算通过率############################
        self.logger.info(f'将本次测试结果汇总整理')
        self.keyId = read(r'./config/temp.yaml')['datetimelist']['datetimename']
        self.createTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        currentresultlist = []
        d = defaultdict(list)
        [d[item['project']].append(item) for item in self.resultlist]
        for k, v in dict(d).items():
            data = json.dumps(v, ensure_ascii=False)
            currentresultlist.append(
                {'keyId': self.keyId, 'createTime': self.createTime, 'project': k, 'detaill': data,
                 'result': json.dumps([res for res in passrate if res['project'] == k][0],
                                      ensure_ascii=False)})
        logger.info(f'最终测试结果：{currentresultlist}')
        ############################ mysql处理部分############################
        if base_cnf['db_mysql']['enable']:
            self.exec_sql = apitest(base_cnf)
            # 将运行错误的用例收集起来
            self.logger.info(f'将测试BUG汇总写入数据库中{currentresultlist}')
            #self.exec_sql.exec_insert_result(['t_api_result_all_v1'], currentresultlist)
        ############################redis处理部分############################
        if Redis:
            self.logger.info(f'将测试BUG汇总写入redis中{currentresultlist}')
            Redis.savedict('errorlist', currentresultlist, '全部测试测试结果与详情写入redis中')
            self.logger.info(f'将临时变量写入redis中')
            Redis.savedict('temp', read(r'./config/temp.yaml'), '保存临时变量')
        ############################企业微信处理部分############################
        qiwechat = base_cnf["qiwechat"]
        if qiwechat['enable']:
            # 推送企业微信消息部分 resultinfo
            self.logger.info(f'推送企业微信消息完成')
            for detaill in passrate:
                #account = [list(item.values())[0]['qiwei_account'] for item in base_cnf['project']['system'] if (list(item.values())[0]['name']) == detaill['project']][0]
                account = [v["qiwei_account"] for _,v in (base_cnf['project']['system']).items() if v["name"] == detaill['project']][0]
                self.logger.info(f'推送企业微信消息细节：{detaill}')
                sendinfo(qiwechat['url'],account,detaill)

        self.logger.info(f'本次测试累计耗时：{total}秒')
        self.logger.info(f'本次测试开始时间 {starttime}')
        self.logger.info(f'本次测试结束时间 {endtime}')
        self.logger.info('执行完毕')

if __name__ == '__main__':
    pass

