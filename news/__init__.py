from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Create the app
app = Flask(__name__)

# Configure the Postgres database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://news_portal:news_portal@127.0.0.1/news_portal'

# Create the extension
db = SQLAlchemy()

# Initialize the app with extension
db.init_app(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
