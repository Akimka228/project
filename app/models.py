from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 
from app import login



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique = True) # индекс
    email = db.Column(db.String(120), unique = True)
    password_hash = db.Column(db.String(120))
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'user {self.username}'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer) # добавить вторичный ключ
    text = db.Column(db.String(120))
    timestamp = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'post {self.text}'


@login.user_loader
def load_user(id):
    return User.query.get(int(id))