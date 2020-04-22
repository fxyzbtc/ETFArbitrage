# -*- coding: utf-8 -*-
import json
from datetime import datetime

# init requests
import requests
import simplejson as json
import sqlalchemy
from json2table import convert
from pytz import timezone
from requests.adapters import HTTPAdapter
from sqlalchemy import or_


from flask import (Blueprint, Flask, flash, redirect, render_template, request,
                   url_for)
from flask.views import MethodView, View
from flask_mail import Mail, Message

from .. import app
from ..mod_mail.forms import SubscriptionForm
from ..mod_mail.models import Subscription
from ..utils import alchemyencoder, Reqs

reqs = Reqs()

class List(View):
    def dispatch_request(self):
        result = json.load(open('taoli.json')) or {'records':[]}
        _time = datetime.strptime('14:00', '%H:%M')
        subform = SubscriptionForm(time=_time, url='/')
        return render_template('taoli/index.html', result=result, subform=subform)


class Top(View):
    def dispatch_request(self):
        return 'show taoli top'

class UpdateTop(View):
    def dispatch_request(self):
        return 'update taoli top'

class Update(View):
    def dispatch_request(self):

        result={'records':[]}
        # 自定义过滤
        def _fs_filter(j):
            if ('万手' in j['tradingAmount']):
                if (float(j['navPriceRatioFcst'].replace('%',''))>=3) or \
                (float(j['navPriceRatioFcst'].replace('%',''))<=-3): # 可申购赎回
                    return True

        #集思录过滤
        def _jsl_filter(item):
            if float(item['cell']['discount_rt'].replace('%','')) >=5 \
            or float(item['cell']['discount_rt'].replace('%','')) <=-3:
                return True
                
        for name in app.config['URLS']: # 按板块
            jsl = reqs.get(app.config['URLS'][name]).json()['rows']
            jsl = [item['id'] for item in jsl if _jsl_filter(item)]

            # 提取fundsmart数据
            for item in jsl: # 提取符合集思录溢价条件的标的
                fs = reqs.get(app.config['TICKER_URL'].format(id=item)).json()

                if _fs_filter(fs):
                    fs = {app.config['HEADERS'][x]:fs[x] for x in app.config['HEADERS']}
                    #dt_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                    #fs['更新时间'] = dt_string
                    result['records'].append(fs)

        #如果有依赖基金，格式化下
        for index,record in enumerate(result['records']):
            if type(record['关联基金']) == list:
                dep_fund = '<br>'.join([','.join(v.values()) for v in record['关联基金']])
                result['records'][index]['关联基金'] = dep_fund

        #open(url_for('static', filename='taoli.json'),'w').write(json.dumps(result))
        open('taoli.json','w').write(json.dumps(result))
        return result


