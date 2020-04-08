# arbitrage
溢价基金套利，懂得自然懂。

# 配置陷阱记录

## uwsgi.ini
```
http = 127.0.0.1:8000
home = /home/ubuntu/arbitrage_test/venv
master = 1
threads = 10
processes = 5
```

如果遇到no module "encoding"等报错，需要重建venv环境即可解决，或者检查home参数设置错误。
```
rm -r venv
pip3 freeze > requirements.txt
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

出现nginx-uwsgi-unavailable-modifier-requested错误，是因为uwsgi依赖python插件
```
sudo apt-get install uwsgi-plugin-python3
```
然后再uwsgi.ini配置文件中添加
```
plugins=python3
```

阅读uwsgi.log看启动日志，能发现python路径等错误。使用相对路径配置ini文件，可以在WSL/不同服务器之间迁移，好的配置样例如下，

```
[uwsgi]
#配合nginx使用
project = arbitrage
#http-socket = 127.0.0.1:8080
socket = /tmp/invest.sock
plugins = python3 #
chdir = %d
home = .env/
module = app:application
#指定工作进程
processes       = 5

#每个工作进程有2个线程
threads = 10
#指的后台启动 日志输出的地方
daemonize       = uwsgi.log
#保存主进程的进程号
pidfile = uwsgi.pid
#虚拟环境环境路径

harakiri = 240 
http-timeout = 240 
socket-timeout = 240 
worker-reload-mercy = 240 
reload-mercy = 240 
mule-reload-mercy = 240

master = 1
```
## nginx.conf
1. 不要使用一个server，在location中尝试用rewrite来达到两个测试服务器，规则太复杂耗时。直接改用两个服务端口对应到不同的测试socket
1. 不要在/etc/nginx/nginx.conf中以引用方式配置server，容易出错且找不到原因（比如一直拉不起8080端口）。
1. 如果设置location的子目录，使用alias不用使用root，否则会在root基础上叠加子目录嵌套

设置两个location, rewrite 头部路径到测试环境
```
server {
        listen 80;
        server_name  _;
        # Load configuration files for the default server block.

        location /books/ {
            alias /home/ubuntu/www/books/;
            autoindex on;
        }

        location / {
            include uwsgi_params;
            uwsgi_pass unix:///tmp/invest.sock;
            uwsgi_read_timeout 120s;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_buffering off;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }
        }

server {
        listen 8080;
        server_name  _x;
        # Load configuration files for the default server block.

        location / {
            include uwsgi_params;
            uwsgi_pass unix:///tmp/invest_test.sock;
            uwsgi_read_timeout 120s;
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_redirect off;
            proxy_buffering off;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }

        }


```

# 开发陷阱

## datetime/time/datetime.datetime/datetime.datetime.time

## sqlalchemy.DateTime/Time Column

## app structure and loading chain

# 常见报错
## Flask No application found
在执行db/mail等扩展时常遇到报错
RuntimeError: No application found. Either work inside a view function or push an application context. See http://flask-sqlalchemy.pocoo.org/contexts/.
可以在命令行中导入flask app_context
```
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'My connection string'
db.init_app(app)

with app.app_context():
    db.create_all()
```

## uwsgi不支持flask调试开关
uwsgi并不会捕捉flask的调试错误，需要这么做：
```
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)
```

## 批量更新SQLAlchemy Model记录
```
entries = []
for item in pepb['entries']:
    entry = PePb(**item)
    entries.append(entry)

#db.session.add_all(entries)
db.session.bulk_save_objects(entries)
db.session.commit()

```

# postgres提示column不存在，实际存在
column名字含有大写字母，需要双引号括起来。
```
select * from "indice" where "stockId"=1000000000995;
```

建议全部改为小写，否则后续sqlalchemy的按列查询也会出错。

