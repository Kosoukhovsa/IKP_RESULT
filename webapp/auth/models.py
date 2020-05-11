from webapp import db
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from sqlalchemy import and_, or_, not_
from datetime import datetime, date
from time import time

# Роли пользователей
roles = db.Table('UserRoles',
    db.Column('user_id',db.Integer,db.ForeignKey('User.id')),
    db.Column('role_id',db.Integer,db.ForeignKey('Role.id'))
)


# Пользователи
class User(db.Model, UserMixin):
    __tablename__ = 'User'
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100),index=True, unique=True)
    clinic_id = db.Column(db.Integer(), db.ForeignKey('Clinic.id'))
    time_create = db.Column(db.DateTime(), default=datetime.utcnow())
    password_hash=db.Column(db.String(128))
    last_visit = db.Column(db.DateTime(), default=datetime.utcnow())
    confirmed=db.Column(db.Boolean(), default=False)
    roles = db.relationship('Role',
                            secondary=roles,
                            backref=db.backref('users', lazy='dynamic'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return(check_password_hash(self.password_hash, password))

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password':self.id, 'exp':time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def has_permissions(self, permission):
        if self.is_admin():
            return True
        for role in self.roles:
            if role.permissions == permission:
                return True
        return False

    def is_admin(self):
        for role in self.roles:
            if role.is_admin == True:
                return True
        return False


    def ping(self):
        self.last_visit = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id= jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def insert_users():
        users = {"admin":{"username":"admin","email":"ikpservicemail@gmail.com","password":"admin","clinic":"1","roles":["ADMIN"]},
                        "doctor":{"username":"doctor","email":"ikp_doctor@gmail.com","password":"doctor","clinic":"1","roles":["HIST_W"]},
                    "researcher":{"username":"researcher","email":"ikp_researcher@gmail.com","password":"researcher","clinic":"1","roles":["DATA_R","DATA_D"]}}
        for (k,v) in users.items():
            user = User.query.filter_by(username=v['username']).first()
            if user:
                continue
            user=User(username=v['username'],email=v['email'])
            user.set_password(v["password"])
            user.clinic_id = v["clinic"]
            for r in v["roles"]:
                role = Role.query.filter_by(permissions=r).first()
                if role:
                    user.roles.append(role)
            try:
                db.session.add(user)
                db.session.commit()
            except Exception:
                db.session.rollback()

# Роли
class Role(db.Model):
    __tablename__ = 'Role'
    id = db.Column(db.Integer(), primary_key=True)
    description = db.Column(db.String(100), unique=True)
    permissions = db.Column(db.String(10), index=True)
    is_admin = db.Column(db.Boolean(), index=True)

    @staticmethod
    def insert_roles():
        roles={'Ведение справочников':{'permission':'REF_W', 'is_admin':False},
                       'Просмотр справочников':{'permission':'REF_R', 'is_admin':False},
                       'Ведение истории болезни':{'permission':'HIST_W', 'is_admin':False},
                       'Чтение истории болезни':{'permission':'HIST_R', 'is_admin':False},
                       'Отчеты просмотр':{'permission':'REP_R', 'is_admin':False},
                       'Отчеты выгрузка':{'permission':'REP_D', 'is_admin':False},
                       'Анализ данных просмотр':{'permission':'DATA_R', 'is_admin':False},
                       'Анализ данных выгрузка':{'permission':'DATA_D', 'is_admin':False},
                       'Администрирование':{'permission':'ADMIN', 'is_admin':True}}
        for (k,v) in roles.items():
            role = Role.query.filter_by(description=k).first()
            if role:
                continue
            role = Role(description=k, permissions=v['permission'],is_admin=v['is_admin'])
            try:
                db.session.add(role)
                db.session.commit()
            except Exception:
                db.session.rollback()
