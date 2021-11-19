import re
from flask.helpers import flash
from app import app 
import os 
from flask import render_template, request, redirect, url_for
from datetime import date
from app import utils
from app import login
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user, login_required
from app import db



@app.route('/')
@app.route ('/index')
@login_required
def index():
    return render_template('index.html', date = str(date.today()), pagename = 'test')


@app.route ('/generator', methods = ['post', 'get'])
def generate():
    if request.method == 'POST':
        form = request.form
        use_number = form.get('use_number')
        pass_len = form.get('password_length')
        use_lower = form.get('use_lower')
        use_spec = form.get('use_spec')
        pass_qty = form.get('passwords_qty')
        passwords = utils.password_gen(pass_len, use_number, use_lower, use_spec, pass_qty)
        for pass_ in passwords:
            flash(pass_)
        return redirect(url_for('generate'))


    return render_template('generator.html')



@app.route ('/login', methods=['post', 'get'])
def login():
    if current_user.is_authenticated: # проверяем, что пользователь авторизован
        return redirect(url_for('index')) # редирект на главную страницу
    if request.method == 'POST': # понимаем, что пришла форма
        form = request.form 
        inputed_username = form.get('username') # берем введенное имя с формы
        inputed_password = form.get('password') # берем введенный пароль с формы
        remember_me = bool(form.get('remember')) 
        user = User.query.filter_by(username=inputed_username).first() # ищем пользователя в БД по username, если user == None, значит пользователь не нашелся
        if user is None or not user.check_password(inputed_password): # если пользователь == None или пароль не прошел проверку  
            return redirect(url_for('login'))
        login_user(user, remember=remember_me)
        # TODO REDIRECT TO REQUESTED PAGE
        return redirect(url_for('index'))
     
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['post', 'get'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        form = request.form 
        inputed_username = form.get('username') # берем введенное имя с формы
        inputed_password = form.get('password')
        inputed_email = form.get('e-mail')
        user = User(username=inputed_username, email=inputed_email)
        user.set_password(inputed_password)
        db.session.add(user)
        db.session.commit()

        # TODO доделать
    return render_template('registration.html')