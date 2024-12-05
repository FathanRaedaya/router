from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'bananasplit"'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'routes')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'jpg'])

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok = True)

db = SQLAlchemy(app)

from app import views, models
from app.models import User
