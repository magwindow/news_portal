from news import app, db
from news.models import Category, Post, Users

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


admin = Admin(app)
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Post, db.session))
admin.add_view(ModelView(Users, db.session))