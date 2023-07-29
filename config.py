import os
import secrets

class Config(object):
    #SECRET_KEY = open('/path/to/secret/file').read()
    SECRET_KEY = SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(16))
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', '587')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    IKP_MAIL_SUBJECT_PREFIX = '[IKP]'
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_USER = os.environ.get('DB_USER')
    DB_USER_PASSWORD = os.environ.get('DB_USER_PASSWORD')


class DevelopmentConfig(Config):
    #DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345qwz@localhost/ikp_dev'

class TestingConfig(Config):
    #DEBUG = True
    #DEBUG_TB_ENABLED = False
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345qwz@localhost:5433/ikp_restore'

class ProductionConfig(Config):
    #SQLALCHEMY_DATABASE_URI = 'postgres://nkvnpwkgmwvbxq:74691526b4438dfe472d020a544a88b5b1777d9735d50a963118ef7238ea09e9@ec2-79-125-26-232.eu-west-1.compute.amazonaws.com:5432/dc13mevsrvuj4j'
    #SQLALCHEMY_DATABASE_URI = 'postgres://'
    # БД на HEROKU
    #SQLALCHEMY_DATABASE_URI = 'postgres://sqdieqjwaeoagh:71f685cb5ad5c30d7c335e087ab918791a7c5b946b1a1be7c183c0679307b381@ec2-54-216-48-43.eu-west-1.compute.amazonaws.com:5432/d1e5qki0kv7tub'
    # БД из бекап
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345qwz@localhost:5432/IKP_DATA'
    #SQLALCHEMY_DATABASE_URI = f'postgres://{Config.DB_USER}:{Config.DB_USER_PASSWORD}@localhost:5432/ikp_data'