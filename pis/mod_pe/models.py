from .. import db
from ..models import Base

class PePb(Base):
    stockid = db.Column(db.BigInteger)
    date = db.Column(db.Date)
    cp = db.Column(db.Float)
    pb = db.Column(db.Float)
    pe_ttm = db.Column(db.Float)


class Indice(Base):
    # New instance instantiation procedure
    stockid = db.Column(db.BigInteger)
    name = db.Column(db.String(20))
    areacode = db.Column(db.String(20))
    stocktype = db.Column(db.String(20))
    exchange = db.Column(db.String(20))
    stockcode = db.Column(db.String(20))
    launchdate = db.Column(db.Date())
    currency = db.Column(db.String(20))
    pb_avgval = db.Column(db.Float) # average
    pb_chanceval = db.Column(db.Float) # 20%
    pb_latestvalpos = db.Column(db.Float) # current val's position
    pb_maxval = db.Column(db.Float)
    pb_maxpositiveval = db.Column(db.Float)
    pb_maxvaldate = db.Column(db.Date)
    pb_medianval = db.Column(db.Float)
    pb_minval = db.Column(db.Float)
    pb_minvaldate = db.Column(db.Date)
    pb_riskval = db.Column(db.Float) # 80%
    pb_latestval = db.Column(db.Float) # current
    pe_ttm_avgval = db.Column(db.Float)
    pe_ttm_chanceval = db.Column(db.Float)
    pe_ttm_latestvalpos = db.Column(db.Float)
    pe_ttm_maxval = db.Column(db.Float)
    pe_ttm_maxvaldate = db.Column(db.Date)
    pe_ttm_maxpositiveval = db.Column(db.Float)
    pe_ttm_medianval = db.Column(db.Float)
    pe_ttm_minval = db.Column(db.Float)
    pe_ttm_minvaldate = db.Column(db.Date)
    pe_ttm_riskval = db.Column(db.Float)
    pe_ttm_latestval = db.Column(db.Float)    