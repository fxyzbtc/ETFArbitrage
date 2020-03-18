from app import db
    
class Subscription(db.Model):
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    time = db.Column(db.Time(), unique=False, nullable=False)
