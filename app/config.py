import os

POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', '')
POSTGRES_DB = os.environ.get('POSTGRES_DB', 'zonemonitor')
POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'postgres')

SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB)
SQLALCHEMY_TRACK_MODIFICATIONS = False

SUSPICIOUS_KEYWORDS = ['bank', 'kredit', 'prihl', 'bezpecn', 'microsoft', 'google']

