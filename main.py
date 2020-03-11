# -*- coding: utf-8 -*-
#import uvicorn
from fastapi import FastAPI
import requests
import simplejson as json
from requests.adapters import HTTPAdapter



URLS = {'ETF':'https://www.jisilu.cn/data/etf/etf_list/?___jsl=LST___',
        'QDII-T0':'https://www.jisilu.cn/data/qdii/qdii_list/?___jsl=LST___',
        'STOCK':'https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___',
        'LOF':'https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___',
}

TICKER_URL = 'https://www.fundsmart.com.cn/api/fund.detail.categroy.php?type=basic&ticker={id}'
TICKER_TAGS = ['name','navPriceRatioFcst', 'navPriceRatio','amplitudes','tradingAmount','application', 'redemption','dependentFundBeans']

app = FastAPI()
s = requests.Session()
s.verify = False
s.mount('http://', HTTPAdapter(max_retries=3))
s.mount('https://', HTTPAdapter(max_retries=3))

@app.get("/taoli")
async def root():
    rows={}
    for name in URLS:
        
        resp = s.get(URLS[name])
        j = resp.json()
        arbitrage_list = j['rows']
        arbitrage_list = [item['id'] for item in arbitrage_list if float(item['cell']['discount_rt'].replace('%','')) >=6]
        
        for item in arbitrage_list:
            j = s.get(TICKER_URL.format(id=item)).json()
            if j['application'] == "1":
                rows['name'] = {item:{x:j[x] for x in TICKER_TAGS}}
    return rows

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)    