# -*- coding: utf-8 -*-
import re
import jieba
import json
# init requests
from flask import render_template
from flask.views import View
from collections import OrderedDict

from ..utils import Reqs
reqs = Reqs()

from .models import FundTrend
from .. import db

# import things
from flask_table import Table, Col
# Declare your table
class ItemTable(Table):
    name = Col('基金主题词')
    count = Col('新基金数量')
    classes = ['table table-striped table-inverse table-responsive']

def _pull_fund():
    KEYS = "债 养老 红利 消费 5G 科技 一带一路 稳健 湾区 健康 通信 医疗 创业板 证券 新能源 汽车 医药 龙头 金融 人工智能 传媒 国企改革 军工 房地产 半导体".split(' ')
    KEYS.extend('交运 仪器 仪表 保险 信托 公用 农牧 制造 券商 化工 医疗 商业 商品 贸易 安防 工程 建设 工艺 建材 房地产 旅游 金属 服务 机械 材料 民航 机场 水泥 水运 汽车 港口 煤炭 物流 环保 玻璃 珠宝 电信 电力 电子 信息 百货 石油 船舶 装修 装饰 设备 金属 软件 配电 运营 通讯 酒店 采选 银行 陶瓷 饲渔 公路'.split(' '))

    URL_TMP = 'http://fund.eastmoney.com/data/FundNewIssue.aspx?t={type}&sort=jzrgq,desc&y=&page=1,100&isbuy=1'
    TYPE = {'xcln':'新成立基金', 'zs':'在售基金'}
    json_re = re.compile(r'\[\[.*\]\]')
    xcln_resp = reqs.get(URL_TMP.format(type='xcln')).text
    _data = json_re.findall(xcln_resp)[0]
    _data = _data.replace(',,', ',0,') # fix none regular data
    data = json.loads(_data)
    zs_resp = reqs.get(URL_TMP.format(type='zs')).text
    data.extend(json.loads(json_re.findall(zs_resp)[0]))

    count = {}
    for fund in data:
        name = fund[1]
        seg_list = jieba.cut(name)
        for key in seg_list:
            try:
                count[key] +=1
            except KeyError:
                count[key] = 1


    db_records = []
    result = {k:v for k,v in count.items() if k in KEYS}
    result = OrderedDict(sorted(result.items(), key=lambda item:item[1], reverse=True))
    for k,v in result.items():
        db_records.append({'topic':k, 'count':v})    
    return db_records

class NewFund(View):
    def dispatch_request(self):
        db_records = _pull_fund()
        return render_template("speculation/index.html", records=db_records)

class ApiNewFund(View):
    def dispatch_request(self):
        db_records = _pull_fund()
        entries = []
        for entry in db_records:
            _entry = FundTrend(**entry)
            entries.append(_entry)
        db.session.bulk_save_objects(entries)
        db.session.commit()
        return {'code':0, 'message':'sync new fund list successfully'}