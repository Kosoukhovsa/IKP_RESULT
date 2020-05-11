from webapp import create_app
from webapp import db
from webapp.auth.models import User, Role
from config import DevelopmentConfig

app = create_app(DevelopmentConfig)
app.app_context().push()
