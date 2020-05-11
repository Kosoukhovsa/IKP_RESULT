import unittest
from webapp import create_app, db
from webapp.admin import admin
from webapp.auth.models import User, Role
from webapp.main.models import Clinic

class TestURLs(unittest.TestCase):
    # Инициализация приложения
    def setUp(self):
        admin._views = []
        self.app = create_app('config.TestingConfig')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        #db.app = app
        db.create_all()
        Clinic.insert_clinic()
        Role.insert_roles()
        User.insert_users()

    # удаление объектов
    def tearDown(self):
        db.session.remove()
        #db.drop_all()
        self.app_context.pop()


    # Добавить пользователя с ролью
    def _insert_user(self, username, password, rolename):
        role = Role.query.filter_by(description=rolename).first()
        user = User.query.filter_by(username=username)
        if user is None:
            user = User()
            user.username = username
            user.set_password(password)
            if role:
                user.roles.append(role)
            db.session.add(user)
            db.session.commit()

    # тест на доступность корневой ссылки приложения
    def test_root_view(self):
        result = self.client.get('/')
        #assert result.status_code == 200
        self.assertEqual(result.status_code,200)

    # Тестирование входа в систему
    def test_login(self):
        self._insert_user('test','test','Ведение истории болезни')
        result = self.client.post('auth/login', data=dict(
                                    username='test',
                                    password='test'), follow_redirects=True)
        #self.assertEqual(db is not None, True)
        self.assertEqual(result.status_code, 200)
        #self.assertIn('You have been loged in', str(result.data))

    # Тестирование неавторизованного входа
    def test_failed_login(self):
        """ Tests failed login """
        self._insert_user('test', 'test', 'Ведение истории болезни')
        result = self.client.post('/auth/login', data=dict(
            username='test',
            password="badpassword"
        ), follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('Invalid username or password', str(result.data))


    def test_unauthorized_access_to_admin(self):
        """ Tests Unauthorized admin access """
        self._insert_user('test', 'test', 'Ведение истории болезни')
        result = self.client.post('/auth/login', data=dict(
            username='test',
            password="test"
        ), follow_redirects=True)
        self.assertEqual(result.status_code, 200)
        result = self.client.get('/admin')
        self.assertEqual(result.status_code, 403)


if __name__ == '__main__':
    unittest.main()
