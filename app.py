from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    """Главная страница"""
    return render_template('news/index.html', title='Главная')


if __name__ == '__main__':
    app.run()
