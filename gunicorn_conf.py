 import multiprocessing
bind = '127.0.0.1:5000'
worker_class = 'gevent'
# # 设置进程文件目录
# pidfile = '/var/run/gunicorn.pid'
# # 设置访问日志和错误信息日志路径
# accesslog = '/var/log/gunicorn_acess.log'
# errorlog = '/var/log/gunicorn_error.log'
# 设置日志记录水平
loglevel = 'warning'

# 并行工作进程数
workers = multiprocessing.cpucount() * 2 + 1
# 处理请求的工作线程数，使用指定数量的线程运行每个worker。为正整数，默认为1。
worker_connections = 2000
# 设置守护进程,将进程交给supervisor管理
daemon = 'false'
