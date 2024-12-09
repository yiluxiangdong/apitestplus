import hashlib


import  requests

# 账号：yangcaibing@tianfu-vip.com
# 密码：SCCP123456!

def  MROtoken(username,password):
    password = bytes(password, 'utf-8')
    hash_object = hashlib.sha1()
    hash_object.update(password)
    password = hash_object.hexdigest()
    url = 'https://mro-api-uat.sunwoda.com/uaa/oauth/token'
    session = requests.session()
    session.headers['Content-Type'] = "application/x-www-form-urlencoded"
    data = {"client_id": "sbuSAHt01SbnftB4",
            "client_secret": "Az4tM5Uyo4dqc6rHdZVhGPgRDpSpxiMXFwaT+6pF54=",
            "grant_type": "password",
            "username": username,
            "password": password
            }

    return session.post(url,data).json()

if __name__ == '__main__':
    print(MROtoken('yangcaibing@tianfu-vip.com','SCCP123456!'))