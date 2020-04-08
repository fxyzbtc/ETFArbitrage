from .. import db
from ..models import Base

class Subscription(Base):
    # New instance instantiation procedure
    def __init__(self, url, email, time):

        self.url = url
        self.email = email
        self.time = time

    def __repr__(self):
        return 'Mail {} to {} at {}'.format(self.url,self.email,self.time)                 

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    time = db.Column(db.Time(), unique=False, nullable=False)
    last_send = db.Column(db.Date())
