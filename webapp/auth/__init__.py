from flask_login import LoginManager, current_user, AnonymousUserMixin
from functools import wraps

class AnonymousUser(AnonymousUserMixin):
    def __init__(self):
        self.user_name = 'Guest'

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'
login_manager.login_messsage = 'Please login to access'
login_manager.login_message_category = 'info'

def create_module(app, **kwargs):
    login_manager.init_app(app)
    from .routes import auth_blueprint
    app.register_blueprint(auth_blueprint)

@login_manager.user_loader
def load_user(userid):
    from .models import User
    return User.query.get(userid)

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_admin():
# Администратору разрешен полный доступ
                return f(*args, **kwargs)
            user_roles = current_user.roles
            for r in user_roles:
                if r.permissions==permission:
                    return f(*args, **kwargs)

            abort(403)

        return decorated_function
    return decorator
