from .. import db
from ..models import Base

class Subscription(Base):
    # New instance instantiation procedure
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    time = db.Column(db.Time(), unique=False, nullable=False)
    last_send = db.Column(db.Date())
