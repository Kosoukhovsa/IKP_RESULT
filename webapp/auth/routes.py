from flask import (Blueprint,
                    current_app,
                    render_template,
                    url_for,
                    flash,
                    redirect,
                    request)
from flask_login import login_user, logout_user, current_user, login_required
from .forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from .models import User, Role
from .email import send_password_reset_email, send_email
from datetime import datetime
from .. import  db


auth_blueprint = Blueprint(
    'auth',
    __name__,
    template_folder='../templates/auth',
    url_prefix='/auth'
)

# Отметка времени о последнем посещении сайта
@auth_blueprint.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()

# Вход в систему
@auth_blueprint.route('/login', methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
                #next = url_for('auth.welcome')
            #flash('You have been loged in', category='info')
            return redirect(next)
        flash('Invalid username or password', category='warning')
    return render_template('login.html', form=form, title='Sign In')

# Выход из системы
@auth_blueprint.route('/logout')
def logout():
    logout_user()
    flash('You are logged out!', category='info')
    return redirect(url_for('main.index'))

# Регистрация
@auth_blueprint.route('/register', methods = ['GET','POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data)
        if user:
            flash('User with email: {} alredy exist'.format(form.email.data))
            return redirect(url_for('.login'))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password1.data)
        user.time_create = datetime.utcnow()
        user.clinic_id = form.clinic.data
        db.session.add(user)
        db.session.commit()
        # Отправить уведомление администратору
        send_email(subject='Зарегистрирован новый пользователь',
                   recipients=[current_app.config['MAIL_ADMIN']],
                   template='admin/event_new_user',
                   user=user)

        flash('You are registered!', category='info')
        return redirect(url_for('.login'))
    return render_template('register.html', title='Register', form=form)

# Запрос на смену пароля
@auth_blueprint.route('/reset_password_request', methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password', category='info')
        else:
            flash('User with email: {} dont exist '.format(form.email.data), category='warning')
        return redirect(url_for('.login'))
    return render_template('reset_password_request.html', form=form, title='Reset password')

# Смена пароля
@auth_blueprint.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user=User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset!', category='info')
        return redirect(url_for('.login'))
    return render_template('reset_password_form.html', form=form, title='Reset password')
