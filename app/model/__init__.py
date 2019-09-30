from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={'enable_baked_queries': True})

from .domain import Domain

