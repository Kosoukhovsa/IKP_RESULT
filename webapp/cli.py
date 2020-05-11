import click
from .auth.models import User, Role
from .main.models import Clinic
from .main import LoadAllDictionary
from . import db



def insert_clinic():
    clinic = Clinic.query.get(1)
    if clinic is None:
        clinic = Clinic('Клинический центр Первого МГМУ им. И.М. Сеченова')
        db.session.add(clinic)
        db.session.commit()
        click.echo('Clinic {0} Added.'.format(clinic.description))

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
            click.echo('Role {0} Added.'.format(role.description))
        except Exception:
            db.session.rollback()

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
            click.echo('User {0} Added.'.format(user.username))
        except Exception:
            db.session.rollback()



def register(app):

    @app.cli.command('generate_test_auth')
    def generate_test_auth():
        insert_clinic()
        insert_roles()
        insert_users()

    @app.cli.command('load_dictionaries')
    def load_dictionaries():
        LoadAllDictionary()
