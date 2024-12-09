# -*- coding:utf-8 -*-
#D:\autoTest\sunwoda\common\getToken.py
import logging
import os
import base64

import jsonpath
import requests
import ddddocr
logger = logging.getLogger(__name__)



def gettoken(username,password):
    datas = {
        "username": username,
        "password": password
    }
    XEncryptionHeader = 'aafdb24427d54695aecd21affef45160'
    url = 'https://service-uat.sunwoda.com'
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
        token = {'Authorization':f"bearer {s.post(url, headers=header,json=data).json()['datas']['access_token']}"}
    except Exception as e:
        token =  {'Authorization':""}
    #删除图片
    if os.path.isfile(file):
        # 删除文件
        os.remove(file)
    else:
        print(f"{file} 文件不存在")

    token.update({
        'X-Encryption-Header': XEncryptionHeader,
        'Employeeno': datas['username'],
        "Content-Type":"application/json;charset=UTF-8",
        "Role-Id":"1701858793090568194",
        "Business-Unit":"Sunwinon"
    })
    return token

if __name__ == '__main__':
    print(gettoken("2204010095","EA[I(AhD0#ms2+&["))
