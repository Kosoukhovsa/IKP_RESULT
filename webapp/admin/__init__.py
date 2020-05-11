from flask_admin import Admin
from webapp.auth.models import Role, User
from webapp.main.models import Clinic, ResearchGroup, Reason, DiagnoseItem, Doctor, Prosthesis, \
                                ProsthesisComponent, Complication, OperationStep, Event, \
                                IndicatorGroup, Indicator, IndicatorDef, IndicatorNorm, Profile, ProfileItem, ProfileAnswer
from .routes import CustomView, CustomModelView, CustomFileAdmin
from .. import db

admin = Admin()

def create_module(app, **kwargs):
    admin.init_app(app)
    admin.add_view(CustomView(name="ИКП"))

    models = [Role, User, Clinic, ResearchGroup, Reason, DiagnoseItem, Doctor, Prosthesis,
              ProsthesisComponent, Complication, OperationStep, Event,
              IndicatorGroup, Indicator, IndicatorDef, IndicatorNorm, Profile, ProfileItem, ProfileAnswer]
    for model in models:
        admin.add_view(CustomModelView(model, db.session, category='Редактирование справочников'))

    admin.add_view(CustomFileAdmin(app.static_folder, '/static/', name='Работа с файлами'))
