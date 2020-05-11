from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp
from .models import User, Role
from ..main.models import Clinic

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(),
    Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
    "Usernames must have only letters, numbers, dots or 'underscores'")])
    email = StringField('Электронная почта', validators=[DataRequired(), Email()])
    clinic = SelectField('Клиника', coerce=int)
    password1 = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password1')])
    submit = SubmitField('Зарегистрироваться')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.clinic.choices=[(clinic.id, clinic.description)
                              for clinic in Clinic.query.order_by(Clinic.id).all()]


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request password reset')

class ResetPasswordForm(FlaskForm):
    password=PasswordField('Password', validators=[DataRequired()])
    password2=PasswordField('Repeat password', validators=[DataRequired(),
                            EqualTo('password')])
    submit=SubmitField('Password reset')

# -- Роли пользователей
class UserRoleForm(FlaskForm):
    user = SelectField('Имя пользователя', coerce = int, validators=[DataRequired()])
    role = SelectField('Роль', coerce = int, validators=[DataRequired()])
    action = RadioField('Действие', choices=[(1,'Добавить'),(2,'Удалить')], default=1, coerce=int)
    submit_ok = SubmitField('Ok')

    def __init__(self, *args, **kwargs):
        super(UserRoleForm, self).__init__(*args, **kwargs)
        self.user.choices=[(user.id, user.username)
                              for user in User.query.order_by(Users.id).all()]
        self.role.choices=[(role.id, role.description)
                              for role in Role.query.order_by(Roles.id).all()]


class UserRoleFilterForm(FlaskForm):
    user_filter = SelectField('Пользователи', coerce = int)
    role_filter = SelectField('Роли', coerce = int)
    submit_filter = SubmitField('Фильтр')

    def __init__(self, *args, **kwargs):
        super(UserRoleFilterForm, self).__init__(*args, **kwargs)
        self.user_filter.choices=[(user.id, user.username)
                              for user in User.query.order_by(User.id).all()]
        self.user_filter.choices.insert(0,(0,'All'))
        self.role_filter.choices=[(role.id, role.description)
                              for role in Role.query.order_by(Role.id).all()]
        self.role_filter.choices.insert(0,(0,'All'))
