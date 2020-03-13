# -*- coding: utf-8 -*-
from flask import Flask, escape, request

import requests
import simplejson as json
from requests.adapters import HTTPAdapter
from json2table import convert

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

@application.route('/taoli/')
def taoli():

    rows={'records':[]}
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

        jsl = [item['id'] for item in jsl if _jsl_filter(item)]

        # 提取fundsmart数据
        for item in jsl: # 提取符合集思录溢价条件的标的
            fs = s.get(TICKER_URL.format(id=item)).json()
            if _fs_filter(fs):
                fs = {HEADERS[x]:fs[x] for x in HEADERS}
                rows['records'].append(fs)


    note_html = "<hr><p>说明:拉取集思录ETF、LOF、股票和QDII列表中的所有折溢价超过6%且交易量>10万手的基金的列表</p>"
    table_attributes = {"border":"1"}
    tbl_html = convert(rows, table_attributes=table_attributes)

    return tbl_html+note_html

if __name__ == "__main__":
    application.run(debug=True)