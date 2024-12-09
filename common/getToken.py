# -*- coding:utf-8 -*-
#D:\autoTest\sunwoda\common\getToken.py
import logging
import os
import base64

import jsonpath
import requests
import ddddocr
from common.commomUtil import read
logger = logging.getLogger(__name__)

def srm_token(s, url, data):
    try:
        Authorization = s.post(url, params=data).json().get('data').get('value')
    except:
        Authorization = None
    return {"Authorization": f"Bearer {Authorization}"}

def dianlian_token(s,project,datas,base_cnf):
    file = 'captcha.png'
    url = base_cnf[project]['url']
    XEncryptionHeader = base_cnf[project]['X-Encryption-Header']
    response = requests.get(f'{url}/api-external/login/validata/code/99ddd')
    data = response.text.split(',')[1]
    image_data = base64.b64decode(data)
    with open(file, 'wb') as f:
        f.write(image_data)
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open(file, 'rb') as f:
        img_bytes = f.read()
    url = f'{url}/api-external/login/uNamePwCaptchaLogin'
    header = {
        'x-encryption-header': XEncryptionHeader
    }
    data = {
      "grant_type": "password",
      "clientId": "webApp",
      "clientSecret": "webApp",
      "verifyCode":ocr.classification(img_bytes),
      "deviceId":"99ddd"
    }
    data.update(datas)
    try:
        token = {
            'Authorization':f"bearer {s.post(url, headers=header,json=data).json()['datas']['access_token']}",
            'X-Encryption-Header': XEncryptionHeader
        }
    except Exception as e:
        token = e
    #删除图片
    if os.path.isfile(file):
        # 删除文件
        os.remove(file)
        print(f"{file} 文件已被删除")

    else:
        print(f"{file} 文件不存在")
    return token

def gettoken(project,datas):
    try:
        base_cnf = read(r'../config/base.yaml')['project']['system']
    except FileNotFoundError:
        base_cnf = read(r'./config/base.yaml')['project']['system']
    try:
        config = read(r'../config/config.yaml')[project]['host']
    except FileNotFoundError:
        config = read(r'./config/config.yaml')[project]['host']
    s = requests.Session()
    file = 'captcha.png'
    url = base_cnf[project]['dianlian']['url']
    if project == 'project_srm':
        return srm_token(s, url+'/cloud-srm/sys/login', datas)
    else:
        XEncryptionHeader = base_cnf[project]['dianlian']['X-Encryption-Header']
        response = requests.get(f'{url}/api-external/login/validata/code/99ddd')
        data = response.text.split(',')[1]
        image_data = base64.b64decode(data)
        with open(file, 'wb') as f:
            f.write(image_data)
        ocr = ddddocr.DdddOcr(show_ad=False)
        with open(file, 'rb') as f:
            img_bytes = f.read()
        url = f'{url}/api-external/login/uNamePwCaptchaLogin'
        header = {
            'x-encryption-header': XEncryptionHeader
        }
        data = {
          "grant_type": "password",
          "clientId": "webApp",
          "clientSecret": "webApp",
          "verifyCode":ocr.classification(img_bytes),
          "deviceId":"99ddd"
        }
        data.update(datas)
        try:
            token = {
                'Authorization':f"bearer {s.post(url, headers=header,json=data).json()['datas']['access_token']}",
                'X-Encryption-Header': XEncryptionHeader,
                # "Deptid": "1685835580611792905",
                # "Orgid": "1685834481767059497"
            }
            #找到对应的部门和组织ID
            if project == 'project_crm':
                result = s.post(config+'/api/crm-server/user/current', json={},headers=token).json()
                jsonpathdata_xs = jsonpath.jsonpath(result, '$..[?(@.name == "销售二部")].orgId')
                jsonpathdata_cw = jsonpath.jsonpath(result, '$..[?(@.name == "财务部门")].orgId')
                jsonpathdata_fw = jsonpath.jsonpath(result, '$..[?(@.name == "法务部")].orgId')
                if jsonpathdata_xs:
                    token['Orgid'] = jsonpathdata_xs[0]
                    token['Deptid'] = jsonpathdata_xs[0]
                if jsonpathdata_cw:
                    token['Orgid'] = jsonpathdata_cw[0]
                    token['Deptid'] = jsonpathdata_cw[0]
                if jsonpathdata_fw:
                    token['Orgid'] = jsonpathdata_fw[0]
                    token['Deptid'] = jsonpathdata_fw[0]
        except Exception as e:
            token = e
        #删除图片
        if os.path.isfile(file):
            # 删除文件
            os.remove(file)
        else:
            print(f"{file} 文件不存在")
        return token

def getcrmtoken(datas):
    XEncryptionHeader = '27f1f90860e94b8facbccdf9bc119fa5'
    url = 'https://service-sit.sunwoda.com'
    host = 'https://crm-sit.sunwoda.com'
    s = requests.Session()
    file = 'captcha.png'
    response = requests.get(f'{url}/api-external/login/validata/code/99ddd')
    data = response.text.split(',')[1]
    image_data = base64.b64decode(data)
    with open(file, 'wb') as f:
        f.write(image_data)
    ocr = ddddocr.DdddOcr(show_ad=False)
    with open(file, 'rb') as f:
        img_bytes = f.read()
    url = f'{url}/api-external/login/uNamePwCaptchaLogin'
    header = {
        'x-encryption-header': XEncryptionHeader
    }
    data = {
      "grant_type": "password",
      "clientId": "webApp",
      "clientSecret": "webApp",
      "verifyCode":ocr.classification(img_bytes),
      "deviceId":"99ddd"
    }
    data.update(datas)
    try:
        token = {
            'Authorization':f"bearer {s.post(url, headers=header,json=data).json()['datas']['access_token']}",
            'X-Encryption-Header': XEncryptionHeader,
        }
    except Exception as e:
        token = e
    #删除图片
    if os.path.isfile(file):
        # 删除文件
        os.remove(file)
    else:
        print(f"{file} 文件不存在")


    #获取对应的部门ID
    deptName = datas.get('deptName')
    if deptName:
        result = s.post(host + '/api/crm-server/user/current', json={}, headers=token).json()
        token['Orgid'] = jsonpath.jsonpath(result, f'$..[?(@.name == "{deptName}")].orgId')[0]
        token['Deptid'] = jsonpath.jsonpath(result, f'$..[?(@.name == "{deptName}")].id')[0]
    return token

if __name__ == '__main__':
    data = {
        "username": "2204010095",
        "password": "123456Aa@@"
    }

    # header = gettoken('crm', data)

    # s = requests.Session()
    # cnf = read(r'E:\sunwoda\config\base.yaml')['dianlian']['crm']
    # cc= 'https://crm-sit.sunwoda.com'
    # a =  s.post(cc+'/api/crm-info/activity/list', headers=header, json={"size":20,"num":1,"userIdList":[]})
    # print(a.json())
    data1 = {
        "username": "2203240012",
        "password": "a83dc2781fb1a2aa54e1e548f91ac7db8b8f1bc0"
    }

    print(gettoken('project_crm',data))














