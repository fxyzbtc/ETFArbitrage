from . import (app, mail, db)
from flask import render_template
from threading import Thread
from flask_mail import Message
import json

import decimal
import datetime

from .mod_pe.models import Indice
def str2headers(headerstr):
    headers = [item for item in headerstr.split('\n') if len(item.replace(' ', '')) >1]
    return {item.split(': ')[0].replace(' ',''):item.split(': ')[1].replace(' ','') for item in headers}

    # authority: www.lixinger.com
    # method: POST
    # path: /api/login/by-account
    # scheme: https
    # accept: application/json, text/plain, */*
    # accept-encoding: gzip, deflate, br
    # accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6
    # content-length: 53
    # content-type: application/json;charset=UTF-8
    # dnt: 1
    # origin: https://www.lixinger.com
    # referer: https://www.lixinger.com/
    # sec-fetch-dest: empty
    # sec-fetch-mode: cors
    # sec-fetch-site: same-origin
    # user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)
 

def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject, sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
    msg.html = render_template(template, **kwargs)
    thrd = Thread(target=async_send_mail, args=[app, msg])
    thrd.start()
    return thrd


def alchemyencoder(obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.time):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, str):
        return str.encode('utf8')

from requests import Session
from requests.adapters import HTTPAdapter
class Reqs(Session):
    def __init__(self):
        Session.__init__(self)
        headerstr = '''User-Agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36
        Accept: text/html,application/json,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        Referer: https://www.google.com/
        Accept-Encoding: gzip, deflate
        Accept-Language: en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6'''
        
        headers = {item.split(':')[0].replace(' ',''):item.split(':')[1].replace(' ','') for item in headerstr.split('\n')}
        self.headers.update(headers)
        self.mount('http://', HTTPAdapter(max_retries=2))
        self.mount('https://', HTTPAdapter(max_retries=2))


class LiXingRener(object):
    def __init__(self):
        import json

        headerstr = '''
                    authority: www.lixinger.com
                    accept: application/json, text/plain, */*
                    accept-encoding: gzip, deflate, br
                    accept-language: en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6
                    content-length: 53
                    content-type: application/json;charset=UTF-8
                    dnt: 1
                    origin: https://www.lixinger.com
                    referer: https://www.lixinger.com/
                    sec-fetch-dest: empty
                    sec-fetch-mode: cors
                    sec-fetch-site: same-origin
                    user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36
                    '''
        headers = str2headers(headerstr)
        self.req = Reqs()        
        self.req.headers.update(headers)
        self.indice_fields = ['stockId', 'name', 'areaCode', 'stockType', 'exchange', 'stockCode', 'launchDate', 'currency']
    
    def login(self, username, password):
        payload = json.dumps({"uniqueName":username,"password":password})
        url = 'https://www.lixinger.com/api/login/by-account'        
        resp = self.req.post(url, data=payload)
        #with cookie
        if resp.status_code == 200:
            return True
        else:
            return False

    def getIndice(self):
        url = 'https://www.lixinger.com/api/analyt/stock-collection/price-metrics/indices/latest'
        payload = json.dumps({"metricNames":["pe_ttm","pb","ps_ttm","dyr","cpc"],"granularities":["f_s"],"metricTypes":["ewpvo"],"source":"all","series":"all","stockFollowedType":"all"})
        resp = self.req.post(url, data=payload)
        
        if resp.status_code == 200:
            return resp.text
        else:
            return {'message': 'getting indice list failed'}

    def getPePb(self, stockId):

        url = 'https://www.lixinger.com/api/analyt/stock-collection/price-metrics/get-price-metrics-chart-info'
        payload = {"stockIds":[stockId],"granularity":"f_s","metricTypes":["ewpvo"],"leftMetricNames":["pe_ttm", "pb"],"rightMetricNames":["cp"]}
        resp = self.req.post(url, data=json.dumps(payload))
        if resp.status_code == 200:
            j = resp.json()
            entries = []
            for item in j['priceMetricsList']:
                #app.logger.info(item)
                entry = {}
                entry['stockid'] = stockId
                
                entry['date'] = datetime.datetime.strptime(item['date'],"%Y-%m-%dT%H:%M:%S.000Z")
                entry['cp'] = item.get('cp')
                entry['pb'] = item.get('pb').get('ewpvo')
                entry['pe_ttm'] = item.get('pe_ttm').get('ewpvo')
                entries.append(entry)

            static = {}
            for item in j['allStatisticsData']:
                for field in j['allStatisticsData'][item]['ewpvo']:
                    if 'Date' in field:
                        static[item+'_'+field.lower()] = datetime.datetime.strptime(j['allStatisticsData'][item]['ewpvo'][field],"%Y-%m-%dT%H:%M:%S.000Z")
                    else:
                        static[item+'_'+field.lower()] = j['allStatisticsData'][item]['ewpvo'][field]

        return {'entries':entries, 'static':static}
        
if __name__ == "__main__":
    pass