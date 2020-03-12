# -*- coding: utf-8 -*-
import uvicorn
from fastapi import FastAPI
import requests
import simplejson as json
from requests.adapters import HTTPAdapter
from json2table import convert
from fastapi.responses import HTMLResponse


URLS = {'ETF':'https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___',
        'QDII-T0':'https://www.jisilu.cn/data/qdii/qdii_list/?___jsl=LST___',
        'STOCK':'https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___',
        'LOF':'https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___',
}

TICKER_URL = 'https://www.fundsmart.com.cn/api/fund.detail.categroy.php?type=basic&ticker={id}'
TICKER_TAGS = ['ticker','name','navPriceRatioFcst', 'navPriceRatio','amplitudes','tradingAmount','application', 'redemption','dependentFundBeans']
TICKER_TAGS_CN = ['代码','名称','折溢价', '昨日折溢价','振幅价差','交易量','申购', '赎回','依赖的基金']
HEADERS = dict(zip(TICKER_TAGS, TICKER_TAGS_CN))

app = FastAPI()
s = requests.Session()
s.verify = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

@app.get("/taoli/")
async def root():
    rows={'list':[]}
    for name in URLS:
        
        resp = s.get(URLS[name])
        j = resp.json()
        arbitrage_list = j['rows']
        arbitrage_list = [item['id'] for item in arbitrage_list if float(item['cell']['discount_rt'].replace('%','')) >=6 or float(item['cell']['discount_rt'].replace('%','')) <=-6]
        
        for item in arbitrage_list:
            j = s.get(TICKER_URL.format(id=item)).json()
            if (float(j['navPriceRatioFcst'].replace('%',''))>=6 and j['application'] == "1") or (float(j['navPriceRatioFcst'].replace('%',''))<=-6 and j['redemption'] == "1"):
                rows['list'].append({HEADERS[x]:j[x] for x in HEADERS})

    note_html = "<hr><p>说明:拉取集思录ETF、LOF、股票和QDII列表中的所有折溢价超过6个百分点的基金的列表</p>"
    table_attributes = {"border":"1"}
    tbl_html = convert(rows, table_attributes=table_attributes)
    return HTMLResponse(content=tbl_html+note_html, status_code=200)

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8888)    