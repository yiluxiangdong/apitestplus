# -*- coding:utf-8 -*-
#D:\autoTest\sunwoda\common\getToken.py
import logging
import os
import base64

import jsonpath
import requests
import ddddocr
logger = logging.getLogger(__name__)



def gettoken(datas):
    XEncryptionHeader = '27f1f90860e94b8facbccdf9bc119fa5'
    url = 'https://service-sit.sunwoda.com'
    host = 'https://crm-sit.sunwoda.com'
    s = requests.Session()
    file = 'captcha.png'
    try:
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
            "verifyCode": ocr.classification(img_bytes),
            "deviceId": "99ddd"
        }
        data.update(datas)


        token = {
            'Authorization':f"bearer {s.post(url, headers=header,json=data).json()['datas']['access_token']}",
            'X-Encryption-Header': XEncryptionHeader,
        }

 #获取对应的部门ID
        deptName = datas.get('deptName')
        if deptName:
            result = s.post(host + '/api/crm-server/user/current', json={}, headers=token).json()
            token['Orgid'] = jsonpath.jsonpath(result, f'$..[?(@.name == "{deptName}")].orgId')[0]
            token['Deptid'] = jsonpath.jsonpath(result, f'$..[?(@.name == "{deptName}")].id')[0]
    except Exception as e:
        token =  {
            'Authorization':"",
            'X-Encryption-Header': XEncryptionHeader,
			'Orgid':"",
			'Deptid':""
        }
    #删除图片
    if os.path.isfile(file):
        # 删除文件
        os.remove(file)
    else:
        print(f"{file} 文件不存在")
    return token

if __name__ == '__main__':
    data = {
        "username": "2204010095",
        "password": "123456Aa@@",
        "deptName": '销售二组-主岗'
    }
    print(gettoken(data))














