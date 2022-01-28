import re
from flask.helpers import flash
from app import app 
import os 
from flask import render_template, request, redirect, url_for
from datetime import date
from app import utils
from app import login
from flask_login import current_user, login_user
from app.models import Post, User
from flask_login import logout_user, login_required
from app import db
from random import *
from datetime import datetime
from app.utils import password_gen, send_mail
import jwt
import json

tokens = []

@app.route('/')
@app.route ('/index')
@app.route('/index/<int:page>')
@login_required
def index(page=1):
    paginated_post = Post.query.order_by(Post.timestamp.desc()).paginate(page, 6, False)
    return render_template('index.html', date = str(date.today()), pagename = 'test', posts=paginated_post)


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
        remember_me = bool(form.get('remember')) # 
        user = User.query.filter_by(username=inputed_username).first() # ищем пользователя в БД по username, если user == None, значит пользователь не нашелся
        if user is None or not user.check_password(inputed_password): # если пользователь == None (т.е. пользователя нет) или пароль не прошел проверку  
            flash('Invalid user or password')
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
        if inputed_email is None:
            inputed_email = str(randint(100000, 999999))
        user = User.query.filter_by(username=inputed_username).first()
        if user is not None:
            flash('This username have been already registered')
            return redirect(url_for('register'))
        user = User(username=inputed_username, email=inputed_email)
        user.set_password(inputed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('registration.html')


@app.route('/user/<requested_username>')
@login_required
def user(requested_username):
    user_from_db = User.query.filter_by(username=requested_username).first_or_404() 
    users_posts = Post.query.filter_by(author=user_from_db)
    print(requested_username)
    return render_template('user.html', user=user_from_db, posts=users_posts)



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow().replace(microsecond=0)
        db.session.commit()


@app.route('/edit_profile', methods = ['POST', 'GET'])
@login_required
def edit_profile():
    if request.method == 'POST':
        form = request.form
        current_user.username = form.get('new_username')
        current_user.about_me = form.get('new_about')
        db.session.commit()
        return redirect(url_for('user', requested_username=current_user.username))
    else: # if send get request
        return render_template('edit_profile.html')
    


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found_error(error):
    return render_template('500.html'), 500

@app.route('/add_post', methods = ['POST', 'GET'])
@login_required
def add_post():
    if request.method == 'POST':
        form = request.form
        post_text = form.get('new_post_text')
        new_post = Post(text=post_text, author=current_user, timestamp=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
        # TODO flash message
    else:
        return render_template('add_post.html')   

@app.route('/reset_password', methods = ['POST', 'GET'])
def reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('/login'))
    if request.method == 'GET':
        return render_template('reset_password.html')
    if request.method == 'POST':
        form = request.form
        inputed_email = form.get('e-mail')
        user = User.query.filter_by(email=inputed_email).first()
        if user is not None:
            generated_password = password_gen(8, True, True, True, 1)[0]
            send_mail(sender='flaskmicroblog63@gmail.com', recepients=[inputed_email], subject='Reset pass', text=generated_password)
            user.set_password(generated_password)
            db.session.commit()
            return redirect('/index')
        else:
            flash('E-mail not found')     
            return redirect(url_for('reset_password'))   

@app.route('/users_list')
def users_list():
    users = User.query.all()
    return render_template('users.html', users = users)

@app.route('/api/login')
def api_login():
    username = request.args['username']
    password = request.args['password']
    user = User.query.filter_by(username=username).first() 
    if user is None or not user.check_password(password):
        return 'Invalid username/password.', 401
    else:
        token = jwt.encode({"user_id": user.id}, "secret", algorithm="HS256")
        tokens.append(token)
        return token, 200

@app.route('/api/register')
def api_register():
    username = request.args['username']
    password = request.args['password']
    email = request.args ['email']
    user = User(username=username, email=email)
    user.set_password(password)    
    try:
        db.session.add(user)
        db.session.commit()
        return 'Register ok', 201
    except:
        return 'Register failed', 500

@app.route('/api/posts')
def get_posts():
    posts = Post.query.all()
    posts_json = []
    for post in posts:
        print(post)
        posts_json.append({
            'id':post.id, 
            'text':post.text,
            'author':post.author.username
        })
    return json.dumps(posts_json)

@app.route('/api/get_user')
def get_user():
    user_id = int(request.args['id'])
    user = User.query.filter_by(id=user_id).first()
    return json.dumps({
        'id':user.id,
        'E-mail':user.email,
        'username':user.username,
        'about_me':user.about_me,
        'avatar_source':user.get_avatar(128)
    })

@app.route('/api/add_post')
def api_add_post():
    post_text = request.args['post_text']
    username = request.args['username']
    user = User.query.filter_by(username=username).first()
    if len(post_text) in range(1, 300):
        new_post = Post(text=post_text, author=user, timestamp=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()
        return 'Post added', 200
    else:
        return 'Post text too long or empty!', 400
@app.route('/api/check_token/<token>')
def check_token(token):
    try:
        token = jwt.decode(token, "secret", algorithm="HS256")
        return token['user_id']
    except:
        return 'User not authorized'