# -*- coding: utf-8 -*-
from .. import (app, db, mail)

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
from .models import Subscription
from ..utils import alchemyencoder

from json2table import convert
import simplejson as json
from datetime import datetime
from pytz import timezone
from flask_mail import Mail
from flask_mail import Message

class Subscribe(View):
    methods = ['POST']
    def dispatch_request(self):
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
                return redirect(url_for('taoli.taoli_list'))

            if 'unsubscribe' in request.form.keys():
                #request.form['unsubscribe']
                record = Subscription.query.filter(Subscription.email == request.form['email']). \
                                            filter(Subscription.url == request.form['url']). \
                                            filter(Subscription.time == request.form['time']).delete()
                db.session.commit()

                _all = Subscription.query.filter(Subscription.email == request.form['email']).all()
                flash('删除成功，已注册信息如下')
                flash(json.dumps([r.as_dict() for r in _all], default = alchemyencoder))
                return redirect(url_for('taoli.taoli_list'))


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
        _json['records'] = [x for x in _json['records'] if len(x['关联基金']) > 10 or 'LOF' in x['name']] #TODO: QDII included in LOF?
        if _json['records']:
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
            else:
                return {'code':1, 'message': 'no subscription found'}
        else:
            return {'code':2, 'message': 'nothing to notify'}