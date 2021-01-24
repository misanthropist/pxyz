from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@127.0.0.1:3306/pxyz"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), unique=True)
    qq = db.Column(db.String(100), unique=True)
    weixin = db.Column(db.String(100), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    uuid = db.Column(db.String(255), unique=True)
    # userlogs = db.relationship('UserLog', backref='user')
    # comments = db.relationship('Comment', backref='user')
    # moviecollects = db.relationship('MovieCollect', backref='user')

    def __repr__(self):
        return "<User %r>" % self.name
    
class UserLog(db.Model):
    __tablename__ = "userlog"
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('userlog', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip = db.Column(db.String(100))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<User %r>" % self.id

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # movies = db.relationship('Movie', backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name

class Movie(db.Model):
    __tablename__ = "movie"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.relationship('Tag', backref=db.backref('movie', lazy='dynamic'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255), unique=True)
    play_num = db.Column(db.BigInteger)
    comment_num = db.Column(db.BigInteger)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # comments = db.relationship('Comment', backref='movie')
    # moviecollects = db.relationship('MovieCollect', backref='movie')
    

    def __repr__(self):
        return "<Movie %r>" % self.title

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    movie = db.relationship('Movie', backref=db.backref('comment', lazy='dynamic'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user = db.relationship('User', backref=db.backref('comment', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Comment %r>" % self.id

class MovieCollect(db.Model):
    __tablename__ = 'moviecollect'
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('moviecollect', lazy='dynamic'))
    movie = db.relationship('Movie', backref=db.backref('moviecollect', lazy='dynamic'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    
    def __repr__(self):
        return "<MovieCollect %r>" % self.id

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    pwd = db.Column(db.String(100))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # adminlogs = db.relationship('AdminLog', backref='admin')

    def __repr__(self):
        return "<Admin %r>" % self.name

class AdminLog(db.Model):
    __tablename__ = "adminlog"
    id = db.Column(db.Integer, primary_key=True)
    admin = db.relationship('Admin', backref=db.backref("adminlog", lazy='dynamic'))
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    ip =  db.Column(db.String(100))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    
    def __repr__(self):
        return "<AdminLog %r>" % self.name