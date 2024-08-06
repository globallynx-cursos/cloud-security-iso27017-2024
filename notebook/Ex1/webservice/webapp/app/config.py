import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql+psycopg2://username:password@postgres_container/dbname'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
