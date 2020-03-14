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
如果遇到no module "encoding"等报错，需要重建venv环境即可解决。
```
rm -r venv
pip3 freeze > requirements.txt
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

## nginx.conf
1. 不要使用一个server，在location中尝试用rewrite来达到两个测试服务器，规则太复杂耗时。直接改用两个服务端口对应到不同的测试socket
1. 不要在/etc/nginx/nginx.conf中以引用方式配置server，容易出错且找不到原因（比如一直拉不起8080端口）。

设置两个location, rewrite 头部路径到测试环境
```
http {
server {
        listen 80;
        server_name  _;
        # Load configuration files for the default server block.

        location / {
            root /home/ubuntu/www/the-economist-ebooks;
            autoindex on;
        }

        location /taoli/ {
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
            root /home/ubuntu/www/the-economist-ebooks;
            autoindex on;
        }

        location /taoli/ {
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
}

```
