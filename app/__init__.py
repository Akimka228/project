from flask import Flask
from flask_sqlalchemy  import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

 
app = Flask(__name__) # объект Flask
app.config['SECRET_KEY'] = 'the random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db' # путь до БД
app.debug = True

db = SQLAlchemy(app) # объект базы данных
migrate = Migrate(app, db) # объект сценариев миграций базы данных 
login = LoginManager(app) # объект системы авторизации
login.login_view = 'login'

from app import routes