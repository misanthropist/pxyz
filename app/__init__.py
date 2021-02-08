from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_redis import FlaskRedis
import os

app = Flask(__name__)
app.debug = True

app.config["SECRET_KEY"] = 'helloworld'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@127.0.0.1:3306/pxyz"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_RECORD_QUERIES"] = True
app.config["DEBUG_TB_PROFILER_ENABLED"] = True
app.config["REDIS_URL"] = 'redis://:@127.0.0.1:6379/0'
# app.config["DEBUG_TB_TEMPLATE_EDITOR_ENABLED"] = True

db = SQLAlchemy(app)
# toolbar = DebugToolbarExtension(app)

rd = FlaskRedis(app)

from app.home import home as home_blueprint
# from app.admin import admin as admin_blueprint

app.register_blueprint(home_blueprint)
# app.register_blueprint(admin_blueprint, url_prefix="/admin")