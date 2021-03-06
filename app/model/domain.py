from sqlalchemy import func

from . import db


class Domain(db.Model):
    __tablename__ = 'domain'

    uid = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(128), nullable=False, unique=True)
    status = db.Column(db.String(32), nullable=False)
    time_added = db.Column(db.DateTime, index=True, nullable=False, default=func.now())
    last_checked = db.Column(db.DateTime, nullable=False, default=func.now())
