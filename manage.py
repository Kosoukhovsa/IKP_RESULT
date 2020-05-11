import os
from dotenv import load_dotenv
from webapp import db, migrate, create_app
from webapp.auth.models import User, Role
from webapp.main.models import Clinic

# Чтение переменной окружения
dotenv_path = os.path.join(os.path.dirname(__file__),'.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Создание приложения с выбранной конфигурацией
env = os.environ.get("APP_CONFIG",default='Development')
app = create_app('config.%sConfig' % env.capitalize())

@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Clinic=Clinic)
