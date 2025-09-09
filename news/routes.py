import os
import uuid

from news import app, db
from forms import PostForm
from models import Post, Category

from werkzeug.utils import secure_filename

from flask import render_template, request, abort, redirect, url_for


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


@app.errorhandler(404)
def page404(e):
    return render_template('news/404.html'), 404
