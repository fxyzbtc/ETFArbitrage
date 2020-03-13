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
TICKER_TAGS_CN = ['代码','名称','折溢价', '昨日折溢价','振幅价差','交易量','申购', '赎回','依赖的基金']
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
                result['records'].append(fs)
    # dd/mm/YY H:M:S
    dt_string = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    result['date'] = dt_string
    open('taoli.json').write(json.dumps(result))
    return result

@application.route('/taoli')
@application.route('/taoli/')
def taoli():
    result = open('taoli.json').read()
    result.simplejson.loads(result)
    return render_template('taoli.html', result=result)

if __name__ == "__main__":
    application.run()