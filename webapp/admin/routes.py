from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import login_required, current_user
from .forms import CKTextAreaField


class CustomView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        return self.render('admin/custom.html')

class CustomModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

class CustomFileAdmin(FileAdmin):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()
