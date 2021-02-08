import datetime
from app import db
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.debug = True

# app.config["SECRET_KEY"] = 'helloworld'
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@127.0.0.1:3306/pxyz"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# db = SQLAlchemy(app)

class Tag(db.Model):
    __tablename__ = 'tag'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # movies = db.relationship('Movie', backref='tag')

    def __repr__(self):
        return "<Tag %r>" % self.name

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    tag = db.relationship('Tag', backref=db.backref('user', lazy='dynamic'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    pwd = db.Column(db.String(100))
    star = db.Column(db.Integer, default=0)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(11), unique=True)
    qq = db.Column(db.String(100), unique=True)
    info = db.Column(db.Text)
    face = db.Column(db.String(255), unique=True)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # uuid = db.Column(db.String(255), unique=True)
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
        return "<UserLog %r>" % self.id

class Item(db.Model):
    __tablename__ = "item"
    id = db.Column(db.Integer, primary_key=True)
    tag = db.relationship('Tag', backref=db.backref('item', lazy='dynamic'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    title = db.Column(db.String(255), unique=True)
    url = db.Column(db.String(255), unique=True)
    info = db.Column(db.Text)
    logo = db.Column(db.String(255), unique=True)
    score = db.Column(db.Integer)
    click_num = db.Column(db.BigInteger)
    comment_num = db.Column(db.BigInteger)
    collect_num = db.Column(db.BigInteger)
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    # comments = db.relationship('Comment', backref='movie')
    # moviecollects = db.relationship('MovieCollect', backref='movie')
    

    def __repr__(self):
        return "<Item %r>" % self.title

class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    item = db.relationship('Item', backref=db.backref('comment', lazy='dynamic'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user = db.relationship('User', backref=db.backref('comment', lazy='dynamic'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return "<Comment %r>" % self.id

class Collect(db.Model):
    __tablename__ = 'collect'
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('collect', lazy='dynamic'))
    item = db.relationship('Item', backref=db.backref('collect', lazy='dynamic'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    add_time = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)

    
    def __repr__(self):
        return "<Collect %r>" % self.id

