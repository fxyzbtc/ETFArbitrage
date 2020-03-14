# -*- coding: utf-8 -*-
from flask import Flask, escape, request
from flask import render_template
from flask import url_for
import requests
import simplejson as json
from requests.adapters import HTTPAdapter
from json2table import convert
from datetime import datetime





URLS = {'ETF':'http://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___',
        'QDII-T0':'http://www.jisilu.cn/data/qdii/qdii_list/?___jsl=LST___',
        'STOCK':'http://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___',
        'LOF':'http://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___',
}

TICKER_URL = 'http://www.fundsmart.com.cn/api/fund.detail.categroy.php?type=basic&ticker={id}'
TICKER_TAGS = ['ticker','name','navPriceRatioFcst', 'navPriceRatio','amplitudes','tradingAmount','application', 'redemption','dependentFundBeans']
TICKER_TAGS_CN = ['代码','名称','今折溢价', '昨折溢价','价格振幅','交易量','申购', '赎回','被依赖基金']
HEADERS = dict(zip(TICKER_TAGS, TICKER_TAGS_CN))

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=2))
s.mount('https://', HTTPAdapter(max_retries=2))

application = Flask(__name__)
application.debug = True


@application.route('/api/taoli/')
def api_taoli():
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

    for name in URLS: # 按板块
        jsl = s.get(URLS[name]).json()['rows']
        application.logger.info('get {}'.format(URLS[name]))
        jsl = [item['id'] for item in jsl if _jsl_filter(item)]

        # 提取fundsmart数据
        for item in jsl: # 提取符合集思录溢价条件的标的
            fs = s.get(TICKER_URL.format(id=item)).json()
            application.logger.info('get {}'.format(TICKER_URL.format(id=item)))
            if _fs_filter(fs):
                fs = {HEADERS[x]:fs[x] for x in HEADERS}
                dt_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                fs['date'] = dt_string
                result['records'].append(fs)

    #如果有依赖基金，格式化下
    for index,record in enumerate(result['records']):
        if type(record['依赖的基金']) == list:
            dep_fund = '<br>'.join([','.join(v.values()) for v in record['依赖的基金']])
            result['records'][index]['依赖的基金'] = dep_fund

    #open(url_for('static', filename='taoli.json'),'w').write(json.dumps(result))
    open('taoli.json','w').write(json.dumps(result))
    return result

@application.route('/taoli')
@application.route('/taoli/')
def taoli():
    result = json.load(open('taoli.json'))
    return render_template('taoli.html', result=result)

if __name__ == "__main__":
    application.run()