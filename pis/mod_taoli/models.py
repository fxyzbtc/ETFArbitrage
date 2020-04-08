from .. import db
from ..models import Base

class Discount(Base):
    # New instance instantiation procedure
    def __init__(self, ticker, date, discount):

        self.ticker = ticker
        self.date = date
        self.discount = discount

    def __repr__(self):
        return '{}-{}-{}'.format(self.ticker,self.date,self.discount)                 

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    ticker = db.Column(db.String(20), nullable=False)
    date = db.Column(db.Date(), nullable=False)
    discount = db.Column(db.Float(), nullable=False)
    freq = db.Column(db.Float())
    source = db.Column(db.String(20))