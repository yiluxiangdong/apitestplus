from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# 创建一个DummyAuthorizer来管理用户账号
authorizer = DummyAuthorizer()
# 添加一个用户，参数依次是：用户名，密码，主目录，权限 
authorizer.add_user('user', '12345', r'/.', perm='elradfmw')

# 将新添加的用户设置为服务器的账号
handler = FTPHandler
handler.authorizer = authorizer

# 定义FTP服务器的地址和端口
address = '0.0.0.0'
port = 88
# 启动FTP服务器
server = FTPServer((address, port), handler)
# 开始监听
server.serve_forever()
