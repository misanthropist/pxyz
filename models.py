from datetime import datetime
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from pxyz.extensions import db


roles_permissions = db.Table('roles_permissions', db.Column('role_id', db.Integer, db.ForeignKey('role.id')), db.Column('permission_id', db.Integer, db.ForeignKey('permission.id')))


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    users = db.relationship('User', back_populates='role', lazy='dynamic')
    permissions = db.relationship('Permission', secondary=roles_permissions, back_populates='roles', lazy='dynamic')

    @staticmethod
    def add_roles(roles_permissions_map):
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)


class Permission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions', lazy='dynamic')


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    follow_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    follow = db.relationship('User', foreign_keys=[follow_id], back_populates='follow_persons', lazy='joined')
    
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed = db.relationship('User', foreign_keys=[followed_id], back_populates='followed_by_persons', lazy='joined')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    receiver = db.relationship('User', foreign_keys=[receiver_id], back_populates='receive_messages', lazy='joined')

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='send_messages', lazy='joined')
    
    @staticmethod
    def push_message(sender, receiver, content):
        message = Message(sender=sender, receiver=receiver, content=content)
        db.session.add(message)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    cover_url = db.Column(db.String(256))
    deleted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    items = db.relationship('Item', back_populates='uploader', cascade='all', lazy='dynamic')
    comments = db.relationship('Comment', back_populates='commenter', cascade='all', lazy='dynamic')
    collections = db.relationship('Collect', back_populates='collector', cascade='all', lazy='dynamic')

    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', back_populates='users')

    send_messages = db.relationship('Message', foreign_keys=[Message.sender_id], back_populates='sender', lazy='dynamic', cascade='all')
    receive_messages = db.relationship('Message', foreign_keys=[Message.receiver_id], back_populates='receiver', lazy='dynamic', cascade='all')

    follow_persons = db.relationship('Follow', foreign_keys=[Follow.follow_id], back_populates='follow', lazy='dynamic', cascade='all')
    followed_by_persons = db.relationship('Follow', foreign_keys=[Follow.followed_id], back_populates='followed', lazy='dynamic', cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_role(self, role):
        self.role = Role.query.filter_by(name=role).first()
    
    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def follow(self, user):
        if not self.is_following(user):
            follow = Follow(follow_id=self.id, followed_id=user.id)
            db.session.add(follow)
    
    def unfollow(self, user):
        follow = self.follow_persons.filter_by(followed_id=user.id).first()
        if follow:
            db.session.delete(follow)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.follow_persons.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        return self.followed_by_persons.filter_by(follower_id=user.id).first()

    def collect(self, item):
        if not self.is_collecting(item):
            collect = Collect(collector_id=self.id, collected_id=item.id)
            db.session.add(collect)

    def uncollect(self, item):
        collect = Collect.query.with_parent(self).filter_by(collected_id=item.id).first()
        if collect:
            db.session.delete(collect)

    def is_collecting(self, item):
        return Collect.query.with_parent(self).filter_by(collected_id=item.id).first() is not None

    def lock(self):
        self.role = Role.query.filter_by(name='Locked').first()

    def unlock(self):
        self.role = Role.query.filter_by(name='User').first()

    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions

    @property
    def is_admin(self):
        return self.role.name == 'Admin'

    @staticmethod
    def add_user(username, password, cover_url="/upload/cover/admin.jpg", role="User"):
        user = User(
            username = username,
            cover_url = cover_url
        )
        user.set_password(password)
        user.set_role(role)
        db.session.add(user)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    file_url = db.Column(db.String(256))
    cover_url = db.Column(db.String(256))
    item_type = db.Column(db.String(16))
    deleted = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uploader = db.relationship('User', back_populates='items')

    comments = db.relationship('Comment', back_populates='item', cascade='all', lazy='dynamic')
    collectors = db.relationship('Collect', back_populates='collected', cascade='all', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Item, self).__init__(**kwargs)

    @staticmethod
    def add_item(title, file_url, cover_url, item_type, username):
        uploader = User.query.filter_by(username=username).first()
        item = Item(
            title = title,
            file_url = file_url,
            cover_url = cover_url,
            item_type = item_type,
            uploader = uploader
        )
        db.session.add(item)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    item = db.relationship('Item', back_populates='comments')
    
    commenter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    commenter = db.relationship('User', back_populates='comments')


class Collect(db.Model):
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    collector_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    collector = db.relationship('User', back_populates='collections')

    collected_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    collected = db.relationship('Item', back_populates='collectors')
