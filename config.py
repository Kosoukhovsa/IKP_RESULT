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
    #DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:12345qwz@localhost/ikp_dev'

class TestingConfig(Config):
    DEBUG = True
    DEBUG_TB_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'postgres://nkvnpwkgmwvbxq:74691526b4438dfe472d020a544a88b5b1777d9735d50a963118ef7238ea09e9@ec2-79-125-26-232.eu-west-1.compute.amazonaws.com:5432/dc13mevsrvuj4j'
    #SQLALCHEMY_DATABASE_URI = 'postgres://'
