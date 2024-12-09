# -*- encoding:utf-8 -*-
#E:\sunwoda\common\config_init.py
import logging
import yaml
from collections import OrderedDict
import yamlordereddictloader

logger = logging.getLogger(__name__)

def initconfig():
    systemname = input("请输入需要创建的系统名称：")
    systemurl = input("请输入需要创建的系统地址：")
    dianlianurl = input("请输入点链系统地址：")
    dianlianheader = input("请输入点链系统请求头：")
    qiwei_account = input("请输入企微工号：")
    mail_account = input("请输入邮箱：")
    rolenumber = input("请输入登录系统的角色数量：")
    rolelist = []
    rolenamelist = []
    rolename = ""
    if int(rolenumber)>1:
        for i in range(int(rolenumber)):
            rolename = input("请输入登录系统的角色：")
            name = input("请输入登录系统的用户名：")
            password = input("请输入登录系统的密码：")
            rolenamelist.append(rolename)
            rolelist.append({f'{rolename}':{"username":name,"password":password}})
        result = {f'project_{systemname}':OrderedDict({"desc":f"{str(systemname).upper()}系统","host":systemurl,"account":rolelist})}
    else:
        name = input("请输入登录系统的用户名：")
        password = input("请输入登录系统的密码：")
        result = {f'project_{systemname}':OrderedDict({"desc":f"{str(systemname).upper()}系统","host":systemurl,"account":{"username":name,"password":password}})}

    data = {"project" : {"desc" : "需要执行项目","system" : [{f"project_{systemname}" : OrderedDict({"enable" : False,"name" : f"{str(systemname).upper()}系统","qiwei_account" : qiwei_account,"mail_account" : {"send" : mail_account,"reception" : mail_account}})}]}}
    dianlian = {"dianlian":{systemname:{"url":dianlianurl,"X-Encryption-Header":dianlianheader}}}

    case = {
        "interfaceName": f'{str(systemname).upper()}系统_模块名称_接口名称',
        "level": "critical",
        "role":rolenamelist[0] if rolename else None,
        "loop": 1,
        "url": "/api-meeting-manager/user/getUserInfo",
        "method": "post",
        "module": "模块名称",
        "function": "功能名称",
        "body": OrderedDict({"queryOrganization1": True, "queryUserRole2": True}),
        "save_key": ["$.datas.userId = userId", "$.datas.organizationId = organizationId"],
        "asserts": ["$.resp_msg == SUCCESS", "$.datas != None", "$.status == 200"]
    }

    # if rolename:
    #     case['role'] = rolenamelist[0]
    #写入用例
    with open(r'E:\sunwoda\databak\configs1.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump([OrderedDict(case)], outfile, Dumper=yamlordereddictloader.Dumper, default_flow_style=False,
                  allow_unicode=True)
    #写入账号配置文件
    with open(r'E:\sunwoda\databak\configs2.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump(OrderedDict(result), outfile, Dumper=yamlordereddictloader.Dumper, default_flow_style=False,
                  allow_unicode=True)
    #写入运行控制文件
    with open(r'E:\sunwoda\databak\configs3.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump(OrderedDict(data), outfile, Dumper=yamlordereddictloader.Dumper, default_flow_style=False,
                  allow_unicode=True)

    #写入点连获取token配置
    with open(r'E:\sunwoda\databak\configs4.yaml', 'w', encoding='utf-8') as outfile:
        yaml.dump(OrderedDict(dianlian), outfile, Dumper=yamlordereddictloader.Dumper, default_flow_style=False,
                  allow_unicode=True)

if __name__ == '__main__':
    initconfig()








