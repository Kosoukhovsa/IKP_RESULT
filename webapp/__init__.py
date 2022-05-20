from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask.helpers import get_root_path
import dash
import dash_bootstrap_components as dbc

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
debug_toolbar = DebugToolbarExtension()

def create_app(object_name):
    """
    Фабрика приложений
    Параметр: объект конфигурации
    Например - config.DevelopmentConfig

    """
    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    debug_toolbar.init_app(app)

    from .auth import create_module as auth_create_module
    from .main import create_module as main_create_module
    from .admin import create_module as admin_create_module
    from .history import create_module as history_create_module
    #from .analytics import create_module as analytics_create_module
    auth_create_module(app)
    main_create_module(app)
    admin_create_module(app)
    history_create_module(app)

    # Добавленние главной страницы аналитики
    from .analytics.homepage import HomePage
    register_dashapps(app, 'Главная страница аналитики', 'analytics/home', HomePage, None)

    # Добавленние аналитического приложения 1 - реестр пациентов
    from .analytics.dashapp11_layout import layout as layout_app_11
    from .analytics.dashapp11_callbacks import register_callback as register_callback_app11
    register_dashapps(app, 'Показатели распределения', 'dashapp1_1',layout_app_11, register_callback_app11)

  # Добавленние аналитического приложения 2 - общая статистика
    from .analytics.dashapp12_layout import layout as layout_app_12
    from .analytics.dashapp12_callbacks import register_callback as register_callback_app12
    register_dashapps(app, 'Общая статистика', 'dashapp1_2',layout_app_12, register_callback_app12)

  # Добавленние аналитического приложения 3 - количественные показатели
    from .analytics.dashapp13_layout import layout as layout_app_13
    from .analytics.dashapp13_callbacks import register_callback as register_callback_app13
    register_dashapps(app, 'Общая статистика', 'dashapp1_3',layout_app_13, register_callback_app13)

  # Добавленние аналитического приложения 4 - качественные показатели
    from .analytics.dashapp14_layout import layout as layout_app_14
    from .analytics.dashapp14_callbacks import register_callback as register_callback_app14
    register_dashapps(app, 'Общая статистика', 'dashapp1_4',layout_app_14, register_callback_app14)


    return app


def register_dashapps(app, title, base_pathname, layout, register_callback_fun):

    # Meta tags for viewport responsiveness
    meta_viewport = {"name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp = dash.Dash(__name__,
                         server=app,
                         url_base_pathname=f'/{base_pathname}/',
                         assets_folder=get_root_path(__name__) + f'/analytics/assets/',
                         #assets_url_path =
                         meta_tags=[meta_viewport],
                         external_stylesheets = [dbc.themes.BOOTSTRAP],
                         #external_stylesheets = [dbc.themes.FLATLY],
                         )

    with app.app_context():
        #dashapp.title = title
        dashapp.layout = layout
        if register_callback_fun is not None:
            register_callback_fun(dashapp)

        #_protect_dashviews(dashapp1)
