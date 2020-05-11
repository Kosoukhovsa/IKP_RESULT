import os
from webapp import create_app
from dotenv import load_dotenv
from webapp.cli import register
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# Чтение переменной окружения для конфигурации из файла .env
dotenv_path = os.path.join(os.path.dirname(__file__),'.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

# Создание приложения с выбранной конфигурацией
env = os.environ.get('APP_CONFIG', default='Development')
app = create_app('config.%sConfig' % env.capitalize())
register(app)



#if __name__ == '__main__':
#    app.run()
