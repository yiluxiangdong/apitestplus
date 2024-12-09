# E:\sunwoda\reportserver\app.py
import datetime
import getpass
import socket
import time
from urllib.request import urlopen
import platform
import os
import sys
import uuid
sys.path.append(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])
import jenkins
import pandas as pd
import sys
from faker import Faker
import uuid
from common.redisUtil import RedisUtil

fake = Faker(locale='zh_CN')
fake1 = Faker(locale='en_US')
sys.path.append("/usr/local/project/api_test/")
from common.commomUtil import getresultbyredis, read, is_excel_yaml_file, write, selectcaseitem, getfileinfo, \
    getloginfo, readdate, updatefile, cleanfile, getnewconf,getmkcookies
from common.dbUtil import apitest as api
from flask import render_template, jsonify, redirect, url_for, send_from_directory, request
from common.getToken import gettoken
from collections import defaultdict
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager, create_refresh_token
from datetime import timedelta
import json
import shutil
import jwt
import subprocess
from flask_cors import CORS, cross_origin
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from common.mrogetToken import MROtoken
from common.zendaoUtil import zendaodb, readexcelcase, readexcelcaseplus

app = Flask(__name__)
from flask import make_response

# 配置日志记录
#handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1, encoding='utf-8')
#handler.setLevel(logging.INFO)

#formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

#handler.setFormatter(formatter)

#app.logger.addHandler(handler)

# app = Flask(__name__)
# Bootstrap(app)
CORS(app, supports_credentials=True, resources=r'/*')  # 解决跨域

'''
nohup python3 app.py runserver -h=0.0.0.0 -p=5070 > run.log 2>&1 &
netstat -tunlp|grep 5070
'''
try:
    CONFIG = read(r'../config/config.yaml')
    CONFIG_CASE = r'../config/casename.yaml'
    CONF = read('../config/base.yaml')
except FileNotFoundError:
    CONFIG = read(r'./config/config.yaml')
    CONFIG_CASE = r'./config/casename.yaml'
    CONF = read('./config/base.yaml')
server = jenkins.Jenkins('https://apitest.sunwoda.com/jenkins', 'root', 'lxb123456')
redis_cnf = CONF['db_redis']
r = RedisUtil(redis_cnf['host'], redis_cnf['port'], redis_cnf['password'])
dircase = r'../databak'
templatedir = r'../files'
dirapp = r'../files'
dirjmx = CONF['jmx']['path_win'] if "windows" in platform.platform().lower() else CONF['jmx']['path_linux']
dirbackup = r'../backup'
applog = r'./'
backupname = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def getfile(filename):
    return f'{dircase}/{filename}'


def buildresult():
    '''
    从redis中获取构建结果
    '''

    resultlist = []
    result = r.getdata('runresult')
    for i in result:
        data = json.loads(i)
        data['detaill'] = json.loads(data['detaill'])
        data['index'] = result.index(i) + 1
        data[
            'createtime'] = f'{data["keyId"][0:4]}-{data["keyId"][4:6]}-{data["keyId"][6:8]} {data["keyId"][8:10]}:{data["keyId"][10:12]}:{data["keyId"][12:14]}'
        resultlist.append(data)
    return resultlist


def buildresult_detaill(jobname, keyId):
    '''
    从redis中获取构建结果
    '''
    resultlist = buildresult()
    d = defaultdict(list)
    [d[items['jobname']].append(items) for items in resultlist]
    data = dict(d).get(jobname)
    for d in data:
        if d['keyId'] == str(keyId):
            # d['keyId'] = f'{d["keyId"][0:3]}-{d["keyId"][4:5]}-{d["keyId"][6:7]} {d["keyId"][8:9]}:{d["keyId"][10:11]}:{d["keyId"][12:13]}'
            return d


def getjob():
    buildslist = []
    result = [builds['name'] for builds in (server.get_all_jobs())]
    for items in result:
        data = server.get_job_info(items)
        buildslist.append(
            {'desc': data['description'], 'name': data['name'], 'url': data['url'], 'index': result.index(items) + 1,
             'count': len(data['builds'])})
    return buildslist


# 检查文件类型是否允许上传
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'yaml', 'xlsx', 'xlsm', 'xls'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.secret_key = 'ChangeMe!'
    CORS(app, supports_credentials=True)  # 解决跨域
    # app.config['JWT_SECRET_KEY'] = 'my_secret_key'
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access']
    app.config['JSON_AS_ASCII'] = False
    # 设置普通JWT过期时间
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30)
    # 设置刷新JWT过期时间
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    jwt = JWTManager(app)
    jwt.init_app(app)
    return app


app = create_app()


@app.route('/sunwodatest/startservices', methods=['POST', 'GET'])
def startservices():
    try:
        subprocess.run(['systemctl', 'start', 'apitest.service'], capture_output=True, text=True)
        if check_server_status():
            return jsonify({'msg': "服务启动成功"})
    except:
        return jsonify({'msg': "服务启动失败"})


@app.route('/sunwodatest/getjobs', methods=['POST', 'GET'])
def getjobs():
    buildslist = []
    result = [builds['name'] for builds in (server.get_all_jobs())]
    for items in result:
        data = server.get_job_info(items)
        buildslist.append(
            {'desc': data['description'], 'name': data['name'], 'url': data['url'], 'index': result.index(items) + 1,
             'count': len(data['builds'])})
    return jsonify({'jobs': buildslist})


@app.route('/sunwodatest/restartservices', methods=['POST', 'GET'])
def restartservices():
    try:
        subprocess.run(['systemctl', 'restart', 'apitest.service'], capture_output=True, text=True)
        if check_server_status():
            return jsonify({'msg': "服务重启成功"})
    except:
        return jsonify({'msg': "服务重启失败"})


@app.route('/sunwodatest/stopservices', methods=['POST', 'GET'])
def stopservices():
    try:
        subprocess.run(['systemctl', 'stop', 'apitest.service'], capture_output=True, text=True)
        if check_server_status():
            return jsonify({'msg': "服务停止成功"})
    except:
        return jsonify({'msg': "服务停止失败"})


def check_server_status():
    try:
        result = subprocess.run(['systemctl', 'status', 'apitest.service'], capture_output=True, text=True)
        status = True if 'Active: active' in result.stdout else False
        return status
    except:
        return True


@app.route('/sunwodatest/login', methods=['POST', 'GET'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    if (username != 'admin' or password != '111111') and (username != 'test' or password != '111111'):
        return jsonify({"msg": "Bad username or password", 'code': 401}), 401
    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)
    rest = {
        'access_token': f"Bearer {access_token}",
        'refresh_token': f"Bearer {refresh_token}",
        'code': 200
    }
    return jsonify(rest)


def setindex(datas):
    result = []
    for i in datas:
        i['index'] = datas.index(i) + 1
        result.append(i)
    return result


def getfiledetaill(dirlist):
    # dirlist = [dircase, dirjmx,applog]
    # dirlist = [dircase, dirjmx]
    from collections import defaultdict
    from itertools import chain
    d = defaultdict(list)
    result = [getfileinfo(path) for path in dirlist if os.path.exists(path)]

    for file in list(chain(*result)):
        d[file['filetype']].append(file)
    return dict(d)


def operation_records(flag, path):
    def generate_records(func):
        def inner(*args, **kwargs):
            r.savedict('recodes', saverecodes(flag, path), flag)
            return func(*args, **kwargs)

        return inner

    return generate_records


def getrecode():
    data = r.getdata('recodes')
    result = [data[i] for i in data]
    recodes = []
    for j in result:
        j['index'] = result.index(j) + 1
        recodes.append(j)
    return sorted(recodes, key=lambda item: item['createtime'], reverse=True)


def getPCinfo(flag, path, types='web') -> dict:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    currentIp = s.getsockname()[0]
    try:
        publicIp = json.load(urlopen('http://httpbin.org/ip'))['origin']
    except:
        publicIp = '0.0.0.0'

    return {
        "type": types,
        "createtime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        "currentIp": currentIp,
        "publicIp": publicIp,
        "UserName": getpass.getuser(),
        "hostName": socket.gethostname(),
        "path": path,
        "info": flag
    }


# 写入操作记录

def saverecodes(msg, path):
    r.savedict('recodes', data={datetime.datetime.now().strftime("%Y%m%d%H%M%S"): getPCinfo('[web端]' + msg, path)},
               msg='[web端]' + msg)


def getcacljob():
    data = {'DFX': [], 'API': []}
    [data['DFX'].append(i) if 'DFX' in i['name'] else data['API'].append(i) for i in getjob()]
    for index in data['DFX']:
        index['index'] = data['DFX'].index(index) + 1
    for index in data['API']:
        index['index'] = data['API'].index(index) + 1
    return data


@app.route('/sunwodatest/homedata', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def homedatas():
    '''
    文件上传
    '''
    jobs = getcacljob()
    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    datas = setindex(files.get('testfile', []))  # 测试文件
    others = setindex(files.get('no_testfile', []))  # 非测试文件
    tempfile = setindex(files.get('tempfile', []))  # 模板文件
    # logfile = setindex([getloginfo(r'./app.log')])  # 模板文件
    stress_testfile = setindex(files.get('stress_testfile', []))  # 压测文件
    server_status = check_server_status()
    result = sorted(buildresult(), key=lambda item: item['createtime'], reverse=True)
    data = {
        'data': datas,
        'DFX': jobs['DFX'],
        'API': jobs['API'],
        'builsresult': result,
        'others': others,
        'tempfile': tempfile,
        'stress_testfile': stress_testfile,
        "server_status": server_status
    }
    saverecodes('登录首页用例管理部分', '/')
    return jsonify(data)


@app.route('/sunwodatest/home1019', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def upload():
    '''
    文件上传
    '''
    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    datas = setindex(files.get('testfile', []))  # 测试文件
    others = setindex(files.get('no_testfile', []))  # 非测试文件
    tempfile = setindex(files.get('tempfile', []))  # 模板文件
    stress_testfile = setindex(files.get('stress_testfile', []))  # 压测文件
    server_status = check_server_status()
    result = sorted(buildresult(), key=lambda item: item['createtime'], reverse=True)
    data = {'data': datas,
            'builsresult': result,
            'others': others,
            'tempfile': tempfile,
            'stress_testfile': stress_testfile,
            "server_status": server_status
            }
    saverecodes('登录首页用例管理部分', '/home')
    return render_template("main.html", data=data)


@app.route('/sunwodatest/home', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def homedata():
    '''
    文件上传
    '''
    jobs = getcacljob()
    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    datas = setindex(files.get('testfile', []))  # 测试文件
    others = setindex(files.get('no_testfile', []))  # 非测试文件
    tempfile = setindex(files.get('tempfile', []))  # 模板文件
    stress_testfile = setindex(files.get('stress_testfile', []))  # 压测文件
    server_status = check_server_status()
    result = sorted(buildresult(), key=lambda item: item['createtime'], reverse=True)
    data = {
        'data': datas,
        'DFX': jobs['DFX'],
        'API': jobs['API'],
        'builsresult': result,
        'others': others,
        'tempfile': tempfile,
        'stress_testfile': stress_testfile,
        "server_status": server_status
    }
    saverecodes('登录首页用例管理部分', '/')
    return render_template("main.html", data=data)
    # return jsonify(data)


@app.route('/sunwodatest/apicase', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def apicase():
    '''
    文件上传
    '''

    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    datas = setindex(files.get('testfile', []))  # 测试文件
    data = {
        'data': datas,
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data), 200


@app.route('/sunwodatest/runcaseinfo', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def runcaseinfo():
    '''
    文件上传
    '''
    jobs = getcacljob()
    app.logger.info('登录首页')
    data = {
        'DFX': jobs['DFX'],
        'API': jobs['API'],
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/builsresult', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def builsresult():
    '''
    文件上传
    '''
    # jobs = getcacljob()
    app.logger.info('登录首页')
    result = sorted(buildresult(), key=lambda item: item['createtime'], reverse=True)
    data = {
        'builsresult': result,
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/othersfiles', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def othersfiles():
    '''
    文件上传
    '''

    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    others = setindex(files.get('no_testfile', []))  # 非测试文件
    data = {
        'others': others,
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/tempfile', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def tempfile():
    '''
    文件上传
    '''

    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    tempfile = setindex(files.get('tempfile', []))  # 模板文件
    data = {
        'tempfile': tempfile,
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/dfxfile', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def dfxfile():
    '''
    文件上传
    '''
    app.logger.info('登录首页')
    files = getfiledetaill([dircase, dirjmx])
    stress_testfile = setindex(files.get('stress_testfile', []))  # 压测文件
    data = {
        'stress_testfile': stress_testfile,
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/serverstatus', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def serverstatus():
    '''
    文件上传
    '''
    app.logger.info('登录首页')
    server_status = check_server_status()
    data = {
        "server_status": server_status
    }
    saverecodes('登录首页用例管理部分', '/home')
    return jsonify(data)


@app.route('/sunwodatest/gettestfile', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def gettestfile():
    '''
    文件上传
    '''
    file = getfiledetaill([dircase, dirjmx])
    app.logger.info('获取文件详情')
    datas = setindex(file.get('testfile', []))  # 测试文件
    others = setindex(file.get('no_testfile', []))  # 非测试文件
    saverecodes('获取文件详情', '/home')
    return jsonify({'testfile': datas, 'othersfile': others, })


@app.route('/sunwodatest/getfile/<filename>', methods=['GET'])
# @operation_records('获取具体文件内容')
def get_data(filename):
    app.logger.info('获取具体文件内容')
    if is_excel_yaml_file(getfile(filename), ['.yaml']):
        data = read(getfile(filename))
    else:
        data = []
        # 使用 pd.ExcelFile 读取文件但不加载数据
        excel_file = pd.ExcelFile(getfile(filename))
        # 获取所有 sheet 名称
        sheet_names = excel_file.sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(getfile(filename), sheet_name=sheet)
            datas = df.to_dict('records')
            data.append({'sheet_names': sheet, 'data': datas})
    saverecodes('获取具体文件内容', f'/getfile/{filename}')
    return jsonify({'msg': json.dumps(data, indent=2, ensure_ascii=False)})


@app.route('/sunwodatest/getfile', methods=['GET', 'POST'])
# @operation_records('获取所有文件内容')
def get_file_data():
    app.logger.info('获取所有文件内容')
    content = request.json
    filename = content.get('filename')
    if is_excel_yaml_file(getfile(filename), ['.yaml']):
        data = read(getfile(filename))
    else:
        data = []
        # 使用 pd.ExcelFile 读取文件但不加载数据
        excel_file = pd.ExcelFile(getfile(filename))
        # 获取所有 sheet 名称
        sheet_names = excel_file.sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(getfile(filename), sheet_name=sheet)
            datas = df.to_dict('records')
            data.append({'sheet_names': sheet, 'data': datas})
    saverecodes('获取所有文件内容', '/getfile')
    return jsonify({'msg': json.dumps(data, indent=2, ensure_ascii=False)})


# @operation_records('下载文件',f'/downfile/')
@app.route('/sunwodatest/downfile/<filename>/', methods=['GET', 'POST'])
def down_data(filename):
    app.logger.info(f'下载文件,/downfile/{filename}')
    saverecodes('下载文件', f'/downfile/{filename}')
    return send_from_directory(f'{dircase}', filename, as_attachment=True)


@app.route('/sunwodatest/downfilejmx/<filename>', methods=['GET', 'POST'])
def down_jmx(filename):
    # filename = request.get_json().get('filename')
    app.logger.info(f'下载文件,/downfile/{filename}')
    saverecodes('下载文件', f'/downfile/{filename}')
    return send_from_directory(f'{dirjmx}', filename, as_attachment=True)


@app.route('/sunwodatest/downfilelog/<filename>/', methods=['GET', 'POST'])
def down_log(filename):
    app.logger.info(f'下载文件,/downfile/{filename}')
    saverecodes('下载文件', f'/downfile/{filename}')
    return send_from_directory(f'{applog}', filename, as_attachment=True)


@app.route('/sunwodatest/downtemplate/<types>', methods=['GET', 'POST'])
def downtemplate(types):
    filepath = templatedir
    app.logger.info(f'下载模板,/downtemplate/{types}')
    if types == "yaml":
        filename = "template.yaml"
    elif types == "app":
        filename = "apitest.exe"
    elif types == "http":
        filename = "http请求模拟器.exe"
    elif types == "xlsm":
        filename = "addtask .xlsm"
    elif types == "configs":
        filename = "config_temp.xlsx"
    else:
        filename = "template.xlsx"
    if os.path.exists(f'{filepath}/{filename}'):
        saverecodes(f'下载{filename}文件', f'/downtemplate/{types}')
        return send_from_directory(f'{filepath}', filename, as_attachment=True)
    else:
        saverecodes(f'下载文件不存在', f'/downtemplate/{types}')
        return jsonify({"msg": f"{filename}文件不存在"})


@app.route('/sunwodatest/selectcase', methods=['GET', 'POST'])
# @operation_records('选择测试用例')
def selectcases():
    app.logger.info(f'选择测试用例,/selectcase/')
    data = request.get_json()
    result = selectcaseitem(data.get('projectName'))
    saverecodes(f'选择测试用例', '/selectcase')
    return jsonify(result)


@app.route('/sunwodatest/delfile', methods=['GET', 'POST'])
# @operation_records('删除文件')
def delfile():
    data = request.get_json()
    filename = data.get('filename')
    app.logger.info(f'删除文件,/delfile/')
    if str(filename).split('.')[-1] == "log":
        os.remove(f'run.log')
    else:
        path = getfile(filename)
        if os.path.exists(path):
            # 备份一下文件
            newname = str(filename).split('.')
            newfiles = f'{newname[0:-1][0]}_{backupname}_备份.{newname[-1]}'
            shutil.copy(getfile(filename), f'{dirbackup}/{newfiles}')
            os.remove(getfile(filename))
    saverecodes(f'删除文件', '/delfile')
    return jsonify({'msg': "删除成功"})


@app.route('/sunwodatest/buildfile', methods=['GET', 'POST'])
# @operation_records('运行用例')
def buildfile():
    data = request.get_json()
    filename = data.get('filename')
    server.build_job(filename)
    app.logger.info(f'运行用例,/buildfile/')
    saverecodes(f'运行用例', '/buildfile')
    return jsonify({'msg': "构建发起成功"})


@app.route('/sunwodatest/buildfileall', methods=['GET', 'POST'])
# @operation_records('运行用例')
def buildfileall():
    data = request.get_json()
    filename = data.get('filename')
    app.logger.info(f'运行全部用例,/buildfileall/')
    with open(CONFIG_CASE, 'w', encoding='utf-8') as f:
        f.truncate()
    server.build_job(filename)
    saverecodes(f'运行用例', '/buildfile')
    return jsonify({'msg': "构建全部发起成功"})


def getrunresult(project, keyId):
    for i in r.getdata('runresult'):
        data = json.loads(i)
        if data['keyId'] == keyId and data['project'] == project:
            return json.loads(json.loads(i)['detaill'])


@app.route('/sunwodatest/getdate/<jobname>/<number>', methods=['POST', 'GET'])
# @operation_records('获取构建信息')
def getdates(jobname, number):
    '''
    文件上传
    '''
    app.logger.info(f'获取构建信息,/getdate/{jobname}/{number}')
    data = getrunresult(jobname, number)
    saverecodes(f'获取构建信息', f'/getdate/{jobname}/{number}')
    return jsonify(data)


@app.route('/sunwodatest/getdate', methods=['POST', 'GET'])
# @operation_records('获取构建详情')
def getdatess(jobname, number):
    '''
    文件上传
    '''
    app.logger.info(f'获取构建详情,/getdate/{jobname}/{number}')
    data = buildresult_detaill(jobname, int(number))
    saverecodes(f'获取构建详情', '/getdate')
    return jsonify(data)


# 处理上传请求

@app.route('/sunwodatest/uploadfile', methods=['POST', 'GET'])
# @operation_records('上传文件')
def uploadfile():
    # 从请求中获取上传的文件
    app.logger.info(f'上传文件,/uploadfile')
    file = request.files['file']
    # 如果文件已经存在，就提示该文件存在
    if str(file.filename).endswith('jmx'):
        filepath = dirjmx
    elif file.filename.startswith("config_temp"):
        filepath = templatedir
    else:
        filepath = dircase

    if not file.filename.startswith("config_temp"):
        if os.path.exists(os.path.join(f'{filepath}', file.filename)):
            return jsonify({'message': '文件已存在', 'status': 'fail', })

    # 检查文件类型是否允许上传
    # if file :
    if file and allowed_file(file.filename):
        # 保存文件到指定路径
        new_file = os.path.join(f'{filepath}', file.filename)
        file.save(new_file)
        if ' ' in file.filename:  # 去掉文件名中的空格
            new_name = file.filename.replace(' ', '')
            os.rename(new_file, os.path.join(f'{filepath}', new_name))
        # 重定向到上传成功页面，并传递文件名参数
        getnewconf(r'../config/config.yaml', os.path.join(f'{filepath}', file.filename).replace('\\', '/'))
        saverecodes(f'上传文件', '/uploadfile')
        return jsonify({'message': '上传成功', 'status': 'success'})

    else:
        # 返回上传失败的提示信息
        saverecodes(f'上传文件失败', '/uploadfile')
        return jsonify({'message': '不支持上传格式，目前只支持yaml, xlsx, xls', 'status': 'fail', })


# 处理上传请求

@app.route('/sunwodatest/uploadfilealltype', methods=['POST'])
# @operation_records('上传文件')
def uploadfilealltype():
    # 从请求中获取上传的文件
    file = request.files['file']
    app.logger.info(f'上传文件,/uploadfilealltype')
    # 如果文件已经存在，就提示该文件存在
    if os.path.exists(os.path.join(f'{dircase}', file.filename)):
        saverecodes(f'上传文件失败', '/uploadfilealltype')
        return jsonify({'message': '文件已存在', 'status': 'fail', })
    # 检查文件类型是否允许上传
    if file:
        # 保存文件到指定路径
        new_file = os.path.join(f'{dircase}', file.filename)
        file.save(new_file)
        if ' ' in file.filename:  # 去掉文件名中的空格
            new_name = file.filename.replace(' ', '')
            os.rename(new_file, os.path.join(f'{dircase}', new_name))
        # 重定向到上传成功页面，并传递文件名参数
        saverecodes(f'上传文件成功', '/uploadfilealltype')
        return jsonify({'message': '上传成功', 'status': 'success'})


@app.route('/sunwodatest/editfile/<filename>')
# @operation_records('编辑文件')
def eidt_data(filename):
    app.logger.info(f'编辑文件,/editfile/{filename}')
    if is_excel_yaml_file(getfile(filename), ['.yaml']):
        data = read(getfile(filename))
    else:
        data = []
        # 使用 pd.ExcelFile 读取文件但不加载数据
        excel_file = pd.ExcelFile(getfile(filename))
        # 获取所有 sheet 名称
        sheet_names = excel_file.sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(getfile(filename), sheet_name=sheet)
            datas = df.to_dict('records')
            data.append({'sheet_names': sheet, 'data': datas})
    saverecodes(f'编辑文件', f'/editfile/{filename}')
    return render_template("edit.html", data=json.dumps(data, indent=2, ensure_ascii=False), types="edit",
                           filename=filename)


@app.route('/sunwodatest/addcases', methods=['GET', 'POST'])
# @operation_records('添加用例')
def addcases():  # 直接html提交过来的
    data = request.json
    filemname = data.get('filemname')
    systemname = data.get('systemname')
    moudlename = data.get('moudlename')
    functionname = data.get('functionname')
    role = data.get('role')
    url = data.get('url')
    method = data.get('method')
    body = data.get('body')
    save_key = [a[0] + "" + "=" + a[1] for a in json.loads(data.get('save_key')) if
                (a[0] != "" or a[1] != "")]
    asserts = [a[0] + "" + a[1] + "" + a[2] for a in json.loads(data.get('asserts')) if
               (a[0] != "" or a[1] != "" or a[2] != "")]

    detaill = [{
        "interfaceName": f'{systemname}_{moudlename}_{functionname}',
        "module": moudlename,
        "systemName": systemname,
        "url": url,
        "function": functionname,
        "role": role,
        "level": "critical",
        "loop": 1,
        "method": method,
        "body": json.loads(body),
        "save_key": save_key,
        "asserts": asserts
    }]

    case = {systemname: detaill}
    # write(f'{dircase}/{filemname}',case)
    if str(filemname).endswith('yaml'):
        updatefile(f'{dircase}/{filemname}', case)
    else:
        # 读取Excel文件
        df = pd.read_excel(f'{dircase}/{filemname}')
        aa = pd.DataFrame(detaill)
        result = aa.append(df, ignore_index=False)
        # 假设df是你要写入Excel的DataFrame
        result.to_excel(f'{dircase}/{filemname}', index=False)
    return jsonify({'msg': "用例添加成功"})


@app.route('/sunwodatest/addcase/<filename>')
# @operation_records('添加用例')
def editfile(filename):
    app.logger.info(f'添加用例,/addcase/{filename}')
    if is_excel_yaml_file(getfile(filename), ['.yaml']):
        data = read(getfile(filename))
    else:
        data = []
        # 使用 pd.ExcelFile 读取文件但不加载数据
        excel_file = pd.ExcelFile(getfile(filename))
        # 获取所有 sheet 名称
        sheet_names = excel_file.sheet_names
        for sheet in sheet_names:
            df = pd.read_excel(getfile(filename), sheet_name=sheet)
            datas = df.to_dict('records')
            data.append({'sheet_names': sheet, 'data': datas})
    saverecodes(f'添加用例', f'/addcase/{filename}')
    return render_template("case.html", filename=filename)
    # return jsonify(json.dumps(data,indent=2,ensure_ascii=False))
    # return render_template("edit.html",data = json.dumps(data,indent=2,ensure_ascii=False),types = "edit",filename = filename)


# 显示上传成功页面

@app.route('/sunwodatest/success')
# @operation_records('上传成功提示')
def success():
    # 获取上传成功页面的文件名参数
    filename = request.args.get('filename')
    # 返回上传成功刷新页面
    saverecodes(f'上传成功提示', '/success')
    return redirect('home')


@app.route('/sunwodatest/returnindex')
# @operation_records('返回首页')
def returnindex():
    # 获取上传成功页面的文件名参数
    # filename = request.args.get('filename')
    # 返回上传成功刷新页面
    saverecodes(f'返回首页', '/returnindex')
    return redirect(url_for('home'))


@app.route('/sunwodatest/submittext', methods=['POST'])
# @operation_records('编辑后提交')
def submit_data():
    content = request.form.get('content')
    filename = request.form.get('filename')
    if filename:
        if is_excel_yaml_file(getfile(filename), ['.yaml']):
            write(getfile(filename), json.loads(content))
        else:
            pass
            # writer = pd.ExcelWriter(getfile(filename), engine='openpyxl')
            # for d in json.loads(content):
            #     df = pd.DataFrame(d['data'])
            #     df.to_excel(writer, sheet_name=d['sheet_names'], index=False)
            # writer.close()
    saverecodes(f'编辑后提交', '/submittext')
    return redirect('home')


from itertools import chain


def formataccount(data):
    account = []
    for i in data:
        datas = []
        for c in i['account']:
            datas.append({"desc": i['desc'], "host": i['host'], "projectName": i['projectName'],
                          'username': list(c.values())[0]['username'], 'password': list(c.values())[0]['password'],
                          'role': list(c.keys())[0]})
        account.append(datas)

    r = list(chain(*account))
    for i in r:
        i['index'] = r.index(i) + 1
    return r


@app.route('/sunwodatest/getconfig', methods=['POST'])
# @operation_records('获取配置信息')
def getconfig():
    saverecodes(f'获取配置信息', '/getconfig')
    resultlist = []
    data1 = read(r'../config/config.yaml')
    for k, v in data1.items():
        if not isinstance(v['account'], list):
            v['account'] = [{'管理员': v.get('account')}]
        v['projectName'] = k
        resultlist.append(v)

    # for k, v in enumerate(data):
    #     data[v]['index'] = k
    #     data[v]['projectName'] = v
    #     resultlist.append(data[v])
    return jsonify({
        "path": r'../config/config.yaml',
        "content": formataccount(resultlist)
    })


@app.route('/sunwodatest/saveconfig', methods=['POST'])
# @operation_records('保存配置信息')
def saveconfig():
    data = request.json
    write(data.get('path'), json.loads(data.get('content')))
    saverecodes(f'保存配置信息', '/saveconfig')
    return jsonify({'msg': '保存成功'})


@app.route('/sunwodatest/getrunconfig', methods=['POST'])
# @operation_records('获取配置信息')
def getrunconfig():
    saverecodes(f'获取配置信息', '/getrunconfig')
    return jsonify({
        "path": r'../config/base.yaml',
        "content": read(r'../config/base.yaml')
    })


@app.route('/sunwodatest/saverunconfig', methods=['POST'])
# @operation_records('获保存配置信息')
def saverunconfig():
    data = request.json
    write(data.get('path'), json.loads(data.get('content')))
    saverecodes(f'获保存配置信息', '/saverunconfig')
    return jsonify({'msg': '保存成功'})


@app.route('/sunwodatest/report/<files>/<project>')
# @operation_records('展示测试报告')
def report_redis(files, project):
    '''
    读取redis
    '''
    # conf = CONF

    if CONF['get_redis']['enable']:
        print('读取redis')
        data = getresultbyredis(files, project)
    else:
        print('读取mysql')
        data = api(CONF).get_report_detaill(files, project)
    result = data['result']
    msg = f"{result['project']}累计运行用列数：{result['total']}条，其中成功{result.get('success', 0)}条，失败{result.get('fail', 0)}条，通过率{result.get('passrate', 0)},其中{result.get('modulepassrate', 0)}"
    saverecodes(f'企微查看测试报告', f'/report/{files}/{project}')
    return render_template("report.html", data=sorted(data['data'], key=lambda item: item['consumetime'], reverse=True),
                           msg=msg, passrate=result['passrate'], keyId=result['keyId'])


@app.route('/sunwodatest/token/<project>', methods=['POST'])
# @operation_records('获取token')
def gettokens(project=None):
    data = {
        "username": request.json.get("username").strip(),
        "password": request.json.get("password").strip()
    }
    projectname = [k for k, v in CONF['project']['system'].items() if v['simplename'] == project][0]
    saverecodes(f'获取token', f'/token/{project}')
    return gettoken(projectname, data)


@app.route('/sunwodatest/updateconf', methods=['POST'])
# @operation_records('获取token')
def updateconf():
    items = request.json.get("items")
    content = json.loads(request.json.get("content"))['detail']
    if json.loads(content) == CONF[items]:
        return jsonify({'msg': '内容无变化'})
    else:
        newfiles = f'base_{backupname}_备份.yaml'
        shutil.copy(r'../config/base.yaml', f'{dirbackup}/{newfiles}')
        CONF[items] = json.loads(content)
        write(r'../config/base.yaml', CONF)
        saverecodes(f'修改运行配置信息{content}', f'/updateconf')
        return jsonify({'msg': CONF})


@app.route('/sunwodatest/updatedb/', methods=['POST'])
# @operation_records('更新数据库')
def updatedb(id=None):
    '''
    更新风险状态
    '''
    from common.pgUtil import pgDB
    pg = pgDB()
    data = request.json
    pg.updateDB(data["id"])
    return jsonify({'msg': "操作成功"})


@app.route('/sunwodatest/userlist', methods=['POST', 'GET'])
# @operation_records('随机生成联系人信息')
def userlist():
    '''
    生成用户信息
    '''
    fake1 = Faker(locale='en_US')
    return jsonify({"userinfolist": [
        {"contacts": fake.name(),"contactsEn": fake1.name(), "phone": fake.phone_number(), "phone1": fake.phone_number(),
         "email": fake.free_email()}
        for _ in range(5)]})


#
# @app.route('/sunwodatest/', methods=['POST', 'GET'])
# def mkcookie():
#     '''
#     生成用户信息
#     '''
#
#     return jsonify({"Cookie": getmkcookie()})


@app.route('/sunwodatest/getuuid')
def getuuid():
    return {"modelId": str(uuid.uuid1()).replace('-', '')[:20].upper(),
            'billId': str(uuid.uuid1()).replace('-', '')[:15].upper()}


@app.route('/sunwodatest/index')
# @operation_records('跳转到登录首页')
def index():
    '''
    文件上传
    '''
    return render_template("main-login.html")


@app.route('/sunwodatest/selectindex', methods=['POST', 'GET'])
# @operation_records('选择需要执行的用例')
def selectindex():
    '''
    文件上传
    '''
    data = request.json
    jobname = data['jobname']
    nolist = data['nolist']
    systemname = data['systemname']
    data = [list(selectcaseitem(jobname).values())[0][i] for i in nolist]
    write(r'../config/casename.yaml', {systemname: data})
    saverecodes("选择需要执行的用例", '/selectindex')
    return jsonify({systemname: data})


@app.route('/sunwodatest/clearcaseunits', methods=['POST', 'GET'])
# @operation_records('选择需要执行的用例')
def clearcaseunits():
    '''
    文件上传
    '''
    cleanfile(r'../config/casename.yaml')
    saverecodes("没有选择用例默认运行全部用例", '/clearcaseunits')
    return jsonify({'msg': '没有选择用例默认运行全部用例'})


@app.route('/sunwodatest/getcmdinfo', methods=['POST', 'GET'])
# @operation_records('获取操作历史记录')
def getcmdinfo():
    '''
    获取操作历史记录
    '''
    data = getrecode()
    saverecodes("获取操作历史记录", '/getcmdinfo')
    return jsonify(data)


@app.route('/sunwodatest/getbaseconf', methods=['POST', 'GET'])
# @operation_records('随机生成联系人信息')
def getbaseconf():
    '''
    获取base配置信息
    '''
    CONFIG = read(r'../config/config.yaml')
    CONF = read('../config/base.yaml')
    saverecodes('获取配置信息', '/getbaseconf')
    return jsonify({"config": CONFIG, "baseconf": CONF})


@app.route('/sunwodatest/getcassedetaills', methods=['POST', 'GET'])
# @operation_records('获取测试用例详情')
def getcassedetaills():
    '''
    获取操作历史记录
    '''

    data = request.json
    saverecodes("获取测试用例详情", '/getcassedetaills')
    filename = data.get("filepath")

    if not str(filename).endswith('yaml'):
        content = readdate(f'{dircase}/{filename}')[0]['data']
    else:
        content = readdate(f'{dircase}/{filename}')
    info = {
        "filename": filename,
        "content": content
    }
    print(info)
    return jsonify(info)


@app.route('/sunwodatest/testapi', methods=['POST', 'GET'])
def testapi():
    '''
    文件上传
    '''
    return render_template("test.html")


@app.route('/sunwodatest/getmenu', methods=['POST', 'GET'])
def getmenu():
    indexdata = {
        'project_crm': {
            "menu": ["通用菜单", "工作台", "团队管理", "市场管理", "线索管理", "商机管理", "需求管理", "客户管理",
                     "合同管理", "回款管理", "报价管理", "统计报表", "系统配置", "系统管理", "个人日程", "任务管理",
                     "销售总结", "跟进记录", "市场资讯", "市场活动", "授权管理"],
            "role": ["销售", "财务", "法务", "交付"]
        },
        'project_otd': {
            "menu": ["预测管理", "单据管理", "客户资料数据", "基础数据", "其他管理", "接口与消息"],
            "role": ["管理员"]
        },
        'project_srm': {
            "menu": ['首页', '供应商管理', '合同管理'],
            "role": ["采购员", "供应商"]
        },
        'project_meet': {
            "menu": ['首页', '会议管理'],
            "role": ["管理员"]
        }
    }

    saverecodes("获取菜单", '/getmenu')
    return jsonify(indexdata)


@app.route('/sunwodatest/runcasebyfilebak', methods=['GET', 'POST'])
def runcasebyfilebak():
    # app.logger.info(f'运行所选文件中的用例,/runcasebyfile')
    data = request.json
    import os
    filename = data.get("filename")
    from common.commomUtil import read, defaultdict, write
    data = read(fr'{dircase}/{filename}')
    d = defaultdict(list)
    for i in data:
        d[i['systemName']].append(i['interfaceName'])
    write(CONFIG_CASE, dict(d))
    commands = \
        [v["jenkinsJob"] for k, v in (CONF["project"]["system"]).items() if v['name'] == list(dict(d).keys())[0]][0]
    dir = str(commands).lower()
    mvcommands = "cp /usr/local/project/api_test/config/casename.yaml /var/lib/jenkins/workspace/{commands}/{dir}/config/casename.yaml"
    os.system(mvcommands)
    mvfilecommands = "cp {dircase}/{filename} /var/lib/jenkins/workspace/{commands}/{dir}/databak"
    os.system(mvfilecommands)
    commands = f"java -jar /usr/local/project/api_test/files/jenkins-cli.jar -s http://apitest.sunwoda.com:8080/jenkins/  -auth root:lxb123456 -webSocket build {commands} -s"
    os.system(commands)
    return jsonify({'msg': f"{filename}文件中{list(dict(d).keys())[0]}用例运行中...."})


@app.route('/sunwodatest/runcasebyfile', methods=['GET', 'POST'])
def runcasebyfiles():
    # app.logger.info(f'运行所选文件中的用例,/runcasebyfile')
    data = request.json
    import os
    filename = data.get("filename")
    from common.commomUtil import read, defaultdict, write
    data = read(fr'{dircase}/{filename}')
    d = defaultdict(list)
    for i in data:
        d[i['systemName']].append(i['interfaceName'])
    write(CONFIG_CASE, dict(d))
    commands = \
        [v["jenkinsJob"] for k, v in (CONF["project"]["system"]).items() if v['name'] == list(dict(d).keys())[0]][0]
    dir = str(commands).lower()
    import platform
    flag = False if 'windows' in platform.platform().lower() else True
    if flag:
        mvcommands = f"cp /usr/local/project/api_test/config/casename.yaml /var/lib/jenkins/workspace/{commands}/{dir}/config/casename.yaml"
        os.system(mvcommands)
        mvfilecommands = f"cp {dircase}/{filename} /var/lib/jenkins/workspace/{commands}/{dir}/databak"
        os.system(mvfilecommands)
    commands = f"java -jar ../files/jenkins-cli.jar -s http://apitest.sunwoda.com:8080/jenkins/  -auth root:lxb123456 -webSocket build {commands} -s"
    os.system(commands)
    return jsonify({'msg': f"{filename}文件中{list(dict(d).keys())[0]}用例运行中...."})


@app.route('/sunwodatest/gettestapi', methods=['POST', 'GET'])
def gettestapi():
    data = request.json
    from common.testcase import apitestcase
    url = data.get("url")
    method = data.get("method")
    body = json.loads(data.get("body"))
    if url == "" or method == "" or body == "":
        result = {'data': {'status': 505}}
    else:
        datas = {
            "url": url,
            "method": method,
            "body": body
        }
        result = apitestcase(f'{data.get("systemname")}', datas)
    if result.get("data").get("status") != 200:
        result = "必填项输入有误或者为空"
    saverecodes("测试一下接口是否成功", '/gettestapi')
    return jsonify({'msg': json.dumps(result, ensure_ascii=False)})


@app.route('/sunwodatest/getproconfig', methods=['POST', 'GET'])
def getproconfig():
    result = [{'items': k, 'desc': v.get('desc', ''), 'value': str(v)} for k, v in CONF.items()]
    saverecodes("获取运行配置信息", '/getproconfig')
    for i in result:
        i['index'] = result.index(i) + 1
    return jsonify(result)


@app.route('/sunwodatest/updatecasecounts', methods=['POST', 'GET'])
def updatecasecount():
    data = request.json
    detaill = json.loads(data.get('data'))
    projectName = detaill['projectName']
    role = detaill['roles']
    username = detaill['username']
    password = detaill['password']
    #username = json.loads(detaill['addaount'])['username']
    #password = json.loads(detaill['addaount'])['password']
    old = CONFIG
    for i in old[projectName]['account']:
        try:
            if role == list(i.keys())[0]:
                i[role]['password']=password
                i[role]['username'] = username
        except:
             old[projectName]['account']['password'] = password
             old[projectName]['account']['username'] = username
             break
    write(r'../config/config.yaml', old)
    return jsonify({'msg': "修改成功"})

#{"projectName":"project_crm","roles":"乙方","username":"crmtest","password":"123456abcd"}
# projectName = detaill['projectName']
# host = detaill['addurl']
# account = json.loads(detaill['addaount'])
#
# if CONFIG[projectName]['account'] == account and CONFIG[projectName]['host'] == host:
#     return jsonify({'msg': '内容无变化'})
# else:
#     newfiles = f'config_{backupname}_备份.yaml'
#     shutil.copy(r'../config/config.yaml', f'{dirbackup}/{newfiles}')
#     CONFIG[projectName]['account'] = account
#     CONFIG[projectName]['host'] = host
#     write(r'../config/config.yaml', CONFIG)
#     saverecodes(f'修改用例配置信息{CONFIG}', f'/updatecasecount')
#     return jsonify({'msg': CONFIG})


def deduplicate(name):
    for project, _ in CONFIG.items():
        if str(project) == str(name):
            return True
    return False


@app.route('/sunwodatest/addcasecounts', methods=['POST', 'GET'])
def addcasecounts():
    data = json.loads(request.json.get('data'))
    projectName = data['addprojectName']
    host = data['addhost']
    account = data['addaccount']
    desc = data['adddesc']
    if deduplicate(projectName):
        return jsonify({'msg': '工程名称重复'})
    else:
        newfiles = f'config_{backupname}_备份.yaml'
        shutil.copy(r'../config/config.yaml', f'{dirbackup}/{newfiles}')
        info = {
            'account': json.loads(account),
            'desc': desc,
            'host': host
        }
        CONFIG[projectName] = info
        write(r'../config/config.yaml', CONFIG)
        saverecodes(f'新增用例配置信息{CONFIG}', f'/addcasecounts')
        return jsonify({'msg': '新增成功'})


@app.route('/sunwodatest/addconfigitems', methods=['POST'])
# @operation_records('获取token')
def addconfigitems():
    data = json.loads(request.json.get('data', None))
    additems = data['additems']
    adddetail = json.loads(data['adddetail'])
    if adddetail == CONF.get(additems):
        return jsonify({'msg': '内容无变化'})
    else:
        newfiles = f'base_{backupname}_备份.yaml'
        shutil.copy(r'../config/base.yaml', f'{dirbackup}/{newfiles}')
        CONF[additems] = adddetail
        write(r'../config/base.yaml', CONF)
        saverecodes(f'修改运行配置信息{adddetail}', f'/updateconf')
        return jsonify({'msg': CONF})


@app.route('/sunwodatest/getjmxfileinfos', methods=['POST'])
# @operation_records('获取token')
def getjmxfileinfos():
    files = getfiledetaill([dirjmx])
    saverecodes(f'获取备份文件信息', f'/getjmxfileinfos')
    print(files)
    return jsonify(files)


@app.route('/sunwodatest/delfilejmxsfiles', methods=['POST'])
# @operation_records('获取token')
def delfilejmxsfiles():
    data = request.get_json()
    filename = data.get('filename')
    os.remove(rf'{dirjmx}/{filename}')
    saverecodes(f'删除压测文件信息', '/delfilejmxsfiles')
    return jsonify({'msg': "删除成功"})


@app.route('/sunwodatest/getcasefileinfos', methods=['POST'])
# @operation_records('获取token')
def getcasefileinfos():
    files = getfiledetaill([dircase])
    saverecodes(f'获取备份文件信息', f'/getcasefileinfos')
    return jsonify(files)


@app.route('/sunwodatest/getbackfileinfos', methods=['POST'])
# @operation_records('获取token')
def getbackfileinfos():
    files = getfiledetaill([r'../backup'])
    saverecodes(f'获取备份文件信息', f'/getbackfileinfos')
    return jsonify(files)


@app.route('/sunwodatest/delfileback', methods=['GET', 'POST'])
# @operation_records('删除文件')
def delfileback():
    data = request.get_json()
    filename = data.get('filename')
    os.remove(rf'../backup/{filename}')
    saverecodes(f'删除备份文件', '/delfileback')
    return jsonify({'msg': "删除成功"})


@app.route('/sunwodatest/getapi', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def getapi():
    '''
    文件上传
    '''
    jobs = getcacljob()
    data = {'DFX': jobs['DFX'], 'API': jobs['API']}
    saverecodes('获取api构建信息', '/getapi')
    return jsonify(data)


@app.route('/sunwodatest/getapicase', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def getapicase():
    '''
    文件查看
    '''
    filename = request.json
    data = readdate(f'../databak/{filename.get("filename")}')
    for item in data:
        item['index'] = data.index(item) + 1
    return jsonify(data)


@app.route('/sunwodatest/getstatus', methods=['GET', 'POST'])
def getstatus():
    status = 0
    return jsonify({'status': status})


@app.route('/sunwodatest/initdata', methods=['GET', 'POST'])
def initdata():
    from common.commomUtil import init_time_args
    return jsonify(init_time_args())


# 禅道相关结果
@app.route('/sunwodatest/createTask', methods=['GET', 'POST'])
def createTask():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    types = request.form.get('type')
    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # 如果文件名是允许的，保存文件
    if file:
        filename = file.filename
        file.save(r'../files/' + filename)  # 保存文件到服务器的指定目录
        datas = readexcelcase(r'../files/' + filename, 0)
        zd = zendaodb(datas[0]["user"])
        result = []
        for items in datas:
            if types == "0":
                jobtype = False
            else:
                jobtype = True
            result.append(
                zd.createTask(jobtype, items["projectInfo"]["project"], items["projectInfo"]["version"], items["data"],
                              items["updatedate"]))
        return jsonify(result)


# 禅道相关结果
@app.route('/sunwodatest/createTaskPlus', methods=['GET', 'POST'])
def createTaskPlus():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    types = request.form.get('type')
    # 如果用户没有选择文件，浏览器也会提交一个没有文件名的空部分
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # 如果文件名是允许的，保存文件
    if file:
        filename = file.filename
        file.save(r'../files/' + filename)  # 保存文件到服务器的指定目录
        datas = readexcelcaseplus(r'../files/' + filename, 0)
        zd = zendaodb(datas[0]["user"])
        result = []
        for items in datas:
            if types == "0":
                jobtype = False
            else:
                jobtype = True
            result.append(
                zd.createTask(jobtype, items["projectInfo"]["project"], items["projectInfo"]["version"], items["data"],
                              items["updatedate"]))
        return jsonify(result)


# 生成公司英文名称
@app.route('/sunwodatest/companyenName', methods=['GET', 'POST'])
def companyenName():
    fake1 = Faker(locale='en_US')
    '''
    生成用户信息
    '''
    return jsonify({
        "companyenName": fake1.company(),
        "bankAccount": '622588' + fake1.credit_card_number(),
        "bankAccount1": '559663' + fake1.credit_card_number(),

    })


import random
import string


@app.route('/sunwodatest/accountinfo', methods=['GET', 'POST'])
def generate_user_info():
    fake1 = Faker(locale='en_US')
    data = {
        "taxCertificateRegistrationNo": fake.random_number(digits=18),
        "telephone": fake.phone_number(),
		"contactsNameEn": fake1.name(),
        "username": fake.name(),
		"companyenName": fake1.company(),
        "customerCode": ''.join(random.choices(string.ascii_uppercase, k=3))
    }
    return jsonify(data)


@app.route('/sunwodatest/crmToken', methods=['POST'])
# @operation_records('获取token')
def getcrmtokens():
    from common.crmgetToken import gettoken
    data = {
        "username": request.json.get("username").strip(),
        "password": request.json.get("password").strip(),
        "deptName": request.json.get("deptName").strip(),
    }
    saverecodes(f'获取crmtoken', f'/crmToken/')
    return gettoken(data)


@app.route('/sunwodatest/mroToken', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def getmroToken():
    '''
    文件查看
    '''
    data = request.json
    username = data.get('username')
    password = data.get('password')
    return MROtoken(username, password)


@app.route('/static/image/<filename>')
def send_image(filename):
    # 假设图片存储在static/images目录下
    return send_from_directory('./static/image', filename)


@app.route('/sunwodatest/newlogin', methods=['POST', 'GET'])
def newlogin():
    return render_template("dist/index.html")

@app.route('/sunwodatest/legalperson', methods=['POST', 'GET'])
def legalperson():
    return jsonify({"contacts": fake.name(), "phone": fake.phone_number(),"taxCertificateRegistrationNo":uuid.uuid1().time})

@app.route('/sunwodatest/forecastDate', methods=['POST', 'GET'])
def forecastDate():
    from common.commomUtil import forecast
    return jsonify(forecast())



@app.route('/sunwodatest/getdatabyjson', methods=['POST', 'GET'])
def  getdatabyjson():
    from  jsonpath import  jsonpath
    datas = request.json
    return jsonpath(datas.get('data'),datas.get('pattern'))



@app.route('/sunwodatest/filedetail', methods=['POST', 'GET'])
def filedetail():
    from common.pgUtil import pgDB
    pgDB = pgDB('apitest')
    return jsonify(pgDB.selectcasedb())

@app.route('/sunwodatest/getcasebyfile', methods=['POST', 'GET'])
def getcasebyfile():
    from common.minioUtil import getcasebyfile
    data = request.json
    filename = data.get('filename')
    return jsonify(getcasebyfile(filename))

@app.route('/sunwodatest/updatecontract', methods=['POST', 'GET'])
def updatecontract():
    data = request.json
    code = data['code']
    status = data['status']
    from common.pgUtilCRM import pgDB
    pg = pgDB('crmcontract')
    try:
        pg.updatecontract(code, status)
        return jsonify({'msg': '更新成功'})
    except:
        return jsonify({'msg': '更新失败'})

@app.route('/sunwodatest/updateprojectlevel', methods=['POST', 'GET'])
def updateprojectlevel():
    data = request.json
    code = data['code']
    level = data['level']
    from common.pgUtilCRM import pgDB
    pg = pgDB('crmserver')
    try:
        pg.updateprojectlevel(code, level)
        return jsonify({'msg': '更新成功'})
    except:
        return jsonify({'msg': '更新失败'})


@app.route('/sunwodatest/getmkcookies', methods=['POST', 'GET'])
def mkcookies():
    data = request.json
    username = data['username']
    password = data['password']
    try:
        return jsonify({'cookies': getmkcookies(username,password)})
    except:
        return jsonify({'cookies': None})


@app.route('/sunwodatest/otdToken', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def getotdToken():
    '''
    文件查看
    '''
    from common.otdgetToken import gettoken
    data = request.json
    username = data.get('username')
    password = data.get('password')
    return gettoken(username, password)

@app.route('/sunwodatest/roundNum', methods=['GET', 'POST'])
# @operation_records('登录首页用例管理部分','/upload')
def roundNum():
    '''
    文件查看
    '''
    from common.commomUtil import rundomNum
    data = request.json
    return rundomNum(int(data.get('rundomNum')),int(data.get('count')))

if __name__ == '__main__':
    # app.run(ssl_context=('server.crt', 'server.key'), host='0.0.0.0', port=8080)
    app.run(ssl_context=(r'/etc/nginx/ssl_key/sunwoda.crt', r'/etc/nginx/ssl_key/sunwoda.key'), host='0.0.0.0',port=5070, debug=True)
    #app.run(host='0.0.0.0', port=5070, debug=True)

