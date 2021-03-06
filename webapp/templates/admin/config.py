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


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345qwz@localhost/robotstat'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://rdjjeqqruepejj:281aa5775fac3cf353e59e7f76915aed835e39014e9b0e9eb12505edcfe4ff2e@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/d6boaecl153lmg'
