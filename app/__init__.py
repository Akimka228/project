from os import truncate
from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager # импорт loginmanager class 
from flask_mail import Mail

 
app = Flask(__name__) # объект Flask
app.config['SECRET_KEY'] = 'the random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # путь до БД
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config ['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'flaskmicroblog63@gmail.com'
app.config['MAIL_PASSWORD'] = 'Flaskmicroblog123'
app.config['MAIL_DEFAULT_SENDER'] = 'flask_app'
app.debug = True

db = SQLAlchemy(app) # объект базы данных
migrate = Migrate(app, db) # объект сценариев миграций базы данных 
login = LoginManager(app) # объект системы авторизации
login.login_view = 'login'
mail = Mail(app)

from app import routes