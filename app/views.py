# -*- coding: utf-8 -*-
from app import app
from app import mail

from flask.views import View
from flask.views import MethodView
from flask import request
from flask import render_template
from flask import url_for
from flask import flash
from flask import redirect

import sqlalchemy
from sqlalchemy import or_

from .forms import SubscriptionForm
from .models import db, Subscription
from .utils import alchemyencoder

from json2table import convert
import simplejson as json
from datetime import datetime
from pytz import timezone
from flask_mail import Mail
from flask_mail import Message

# init requests
import requests
from requests.adapters import HTTPAdapter
s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=2))
s.mount('https://', HTTPAdapter(max_retries=2))

class TaoLi(View):
    def dispatch_request(self):
        result = json.load(open('taoli.json')) or {'records':[]}
        _time = datetime.strptime('14:00', '%H:%M')
        subform = SubscriptionForm(time=_time, url='/taoli/')
        return render_template('taoli.html', result=result, subform=subform)

class Subscribe(View):
    def dispatch_request(self):
        if request.method == 'GET':
            return 'subscribe [GET]'

        if request.method == 'POST':
            if 'subscribe' in request.form.keys():
                #request.form['subscribe']:
                subform = SubscriptionForm(request.form)
                subscription = Subscription()
                #subscription.time = timezone('Asia/Shanghai').localize(Subscription.time)
                subform.populate_obj(subscription)
                # 只允许注册一次 email + url
                if Subscription.query.filter(Subscription.email == request.form['email']). \
                                        filter(Subscription.url == request.form['url']).all():
                    _all = Subscription.query.filter(Subscription.email == request.form['email']).all()                
                    flash('已经注册，信息如下')
                    flash(json.dumps([r.as_dict() for r in _all], default = alchemyencoder))
                else:
                    db.session.add(subscription)
                    db.session.commit()
                #except sqlalchemy.exc.IntegrityError:
                #    flash('已经注册')
                #    db.session.rollback()
                    flash('注册成功')
                return redirect(url_for('show_taoli'))

            if 'unsubscribe' in request.form.keys():
                #request.form['unsubscribe']
                record = Subscription.query.filter(Subscription.email == request.form['email']). \
                                            filter(Subscription.url == request.form['url']). \
                                            filter(Subscription.time == request.form['time']).delete()
                db.session.commit()

                _all = Subscription.query.filter(Subscription.email == request.form['email']).all()
                flash('删除成功，已注册信息如下')
                flash(json.dumps([r.as_dict() for r in _all], default = alchemyencoder))
                return redirect(url_for('show_taoli'))


class ApiTaoLi(View):
    def dispatch_request(self):

        result={'records':[]}
        # 过滤集思录数据
        def _fs_filter(j):
            if ('万手' in j['tradingAmount']):
                if (float(j['navPriceRatioFcst'].replace('%',''))>=6 and j['application'] == "1") or \
                (float(j['navPriceRatioFcst'].replace('%',''))<=-6 and j['redemption'] == "1"): # 可申购赎回
                    return True

        def _jsl_filter(item):
            if float(item['cell']['discount_rt'].replace('%','')) >=6 \
            or float(item['cell']['discount_rt'].replace('%','')) <=-6:
                return True

        for name in app.config['URLS']: # 按板块
            jsl = s.get(app.config['URLS'][name]).json()['rows']
            jsl = [item['id'] for item in jsl if _jsl_filter(item)]

            # 提取fundsmart数据
            for item in jsl: # 提取符合集思录溢价条件的标的
                fs = s.get(app.config['TICKER_URL'].format(id=item)).json()

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

class NotifyAll(View):
    def dispatch_request(self):
        '''LOF in name or etfFeeders not --此时可以套利或者降成本操作'''
        
        tz_china = timezone('Asia/Shanghai')
        tz_utc = timezone('UTC')
        utc = datetime.utcnow().replace(tzinfo=tz_utc)
        _time = utc.astimezone(tz_china)
        time_china = datetime.time(_time)
        date_china = datetime.date(_time)

        #exclude taoli.json with none etffeeders
        _json = json.load(open('taoli.json'))
        _json['records'] = [x for x in _json['records'] if len(x['关联基金']) > 10]
        table_attributes = {"border":1}
        mail_html = convert(_json, table_attributes=table_attributes)

        subscriptions = Subscription.query.filter(or_(Subscription.last_send == None, Subscription.last_send != date_china)). \
                                            filter(Subscription.time <= time_china).all()

        if subscriptions:
            
            app.logger.info('invest::preparing to send mail to {} subscriptions'.format(len(subscriptions)))
            for sub in subscriptions:
                addr = sub.email
                subject = '折溢价基金套利提醒{}'.format(date_china)
                recipients=[addr]
                sender = 'molartech2020@gmail.com'
                msg = Message(subject,recipients=recipients)
                msg.html = "<p>请<a href={host}taoli/>点击这里</a>查看详情</p><hr>{html}".format(host=request.host_url, html=mail_html)
                mail.send(msg)
                app.logger.info('invest::sent mail to {}'.format(addr))
                #更新last_send date, 1 mail/day
                sub.last_send = date_china
                db.session.commit()
        
        return 'mails sent to {} subscriptions'.format(len(subscriptions))