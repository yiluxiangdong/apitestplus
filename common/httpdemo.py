# -*- encoding:utf-8 -*-
import requests
import os

def httpget():
    data = requests.get(url = 'https://ipaas-external-uat.sunwoda.com/financialsharing/v1/platform/data-model/api_manage/info/get-by-id/1579352192909414400',headers={"appkey":"667bafb02888ce5a3c65fa35"}).json()
    print(data)

# 例如，列出当前目录下的文件和文件夹

def  commandJenkins(command):
    dir = str(command).lower()
    mvcommands = "mv /usr/local/project/api_test/config/casename.yaml /var/lib/jenkins/workspace/{command}/{dir}/config/casename.yaml"
    os.system(mvcommands)
    commands = f"java -jar /usr/local/project/api_test/files/jenkins-cli.jar -s http://localhost:8080/  -auth root:lxb123456 -webSocket build {command} -s"
    exit_code = os.system(commands)
    if exit_code == 0:
       return True
    else:
       return False
if __name__ == '__main__':
    commandJenkins("SRM-API-test")

 