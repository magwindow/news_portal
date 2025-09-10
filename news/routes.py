import os
import uuid

from news import app, db
from news.forms import PostForm, Registration, UserLogin
from news.models import Post, Category, Users

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.exc import IntegrityError

from flask import render_template, request, abort, redirect, url_for
from flask_login import LoginManager, login_user, logout_user

# Flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'


@login_manager.user_loader
def load_user(user_id):
    """Чекер пользователя"""
    return Users.query.get(int(user_id))


@app.route('/login', methods=['POST', 'GET'])
def user_login():
    """Аутентификация пользователя"""
    form = UserLogin(request.form)
    if request.method == 'POST':
        user = Users.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))

    return render_template('news/user_login.html', form=form)


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['POST', 'GET'])
def user_registration():
    """Логика для регистрации"""
    form = Registration(request.form)

    if request.method == 'POST' and form.validate():
        password_hash = generate_password_hash(form.password.data, method='scrypt')
        user = Users(first_name=form.first_name.data,
                     last_name=form.last_name.data,
                     username=form.username.data,
                     phone=form.phone.data,
                     email=form.email.data,
                     password=password_hash)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    return render_template('news/user_registration.html', form=form)


@app.route('/')
@app.route('/index')
def index():
    """Главная страница"""
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('news/index.html',
                           title='Главная',
                           posts=posts,
                           categories=categories)


@app.route('/category/<int:id>')
def category_list(id: int):
    """Реакция на нажатие кнопок категории"""
    categories = Category.query.all()
    posts = Post.query.filter(Post.category_id == id)
    current = Category.query.get(id)
    return render_template('news/index.html',
                           title=current,
                           categories=categories,
                           posts=posts,
                           current=current)


@app.route('/post/<int:id>')
def post_detail(id: int):
    """Статья на отдельной странице"""
    post = Post.query.filter(Post.id == id).first()
    return render_template('news/post_detail.html', post=post)


@app.route('/search/', methods=['GET'])
def search_result():
    """Для поиска"""
    q = request.args.get('q')
    categories = Category.query.all()
    search = Post.title.contains(q) | Post.content.contains(q)
    posts = Post.query.filter(search).all()
    if not posts:
        abort(404)
    return render_template('news/index.html',
                           categories=categories,
                           posts=posts)


@app.route('/post/create', methods=['POST', 'GET'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        category_id = Category.query.filter(Category.title == category).first().id

        picture_file = request.files['picture']
        picture_name = secure_filename(picture_file.filename)
        picture_name = str(uuid.uuid1()) + '_' + picture_name
        picture_file.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))

        post = Post(title=title,
                    content=content,
                    category_id=category_id,
                    picture=picture_name)
        db.session.add(post)
        db.session.commit()

        return redirect(url_for('category_list', id=category_id))

    categories = Category.query.all()
    form = PostForm()
    form.category.choices = [cat.title for cat in categories]

    return render_template('news/create_post.html', form=form)


@app.route('/post/<int:id>/delete/')
def delete_post(id: int):
    """Удаление поста"""
    post = Post.query.get(id)
    category = post.category_id
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('category_list', id=category))


@app.route('/post/<int:id>/update/', methods=['POST', 'GET'])
def update_post(id: int):
    """Кнопка редактировать"""
    post = Post.query.get(id)
    categories = Category.query.all()
    if request.method == 'POST':
        category = request.form['category']
        category_id = Category.query.filter(Category.title == category).first().id
        post.category_id = category_id
        post.title = request.form['title']
        post.content = request.form['content']

        if picture_file := request.files['picture']:
            picture_name = secure_filename(picture_file.filename)
            picture_name = str(uuid.uuid1()) + '_' + picture_name
            picture_file.save(os.path.join(app.config['UPLOAD_FOLDER'], picture_name))
            post.picture = picture_name

        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post_detail', id=id))

    form = PostForm(obj=post)
    form.category.choices = [cat.title for cat in categories]
    return render_template('news/create_post.html', form=form, id=id)


@app.errorhandler(404)
def page404(e):
    return render_template('news/404.html'), 404
