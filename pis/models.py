from . import db

# Define a base model for other database tables to inherit
class Base(db.Model):
    __abstract__  = True

    id            = db.Column(db.Integer, primary_key=True)
    date_created  = db.Column(db.DateTime,  default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime,  default=db.func.current_timestamp(),
                    onupdate=db.func.current_timestamp())

    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}
      
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)