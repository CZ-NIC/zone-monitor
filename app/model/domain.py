from . import db

class Domain(db.Model):
    __tablename__ = 'domain'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    status = db.Column(db.String(16))

