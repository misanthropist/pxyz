import os
from flask import Blueprint, render_template, session, request, redirect, flash, url_for, current_app
from sqlalchemy import or_
from pxyz.models import Message, User
from pxyz.extensions import db
from pxyz.decorators import login_require

message_bp = Blueprint('message', __name__)

@message_bp.route('/message/')
@message_bp.route('/message/<int:page>/')
@login_require
def index(page=1):
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    pagination = Message.query.filter(or_(Message.receiver == user, Message.sender == user)).order_by(Message.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
    return render_template('message/index.html', pagination=pagination, user=user)

@message_bp.route('/message/', methods=['POST'])
@message_bp.route('/message/<int:page>/', methods=['POST'])
@login_require
def send():
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    if request.form:
        receiver = request.form.get('receiver')
        receiver = User.query.filter_by(username=receiver).first()
        send_content = '<a href="{}">{}</a> 向 <a href="{}">{}</a> 发送消息：{}'.format(url_for('user.index', user_id=user.id), user.username, url_for('user.index', user_id=receiver.id), receiver.username, request.form.get('send_content'))
        if receiver and send_content:
            Message.push_message(user, receiver, send_content)
            db.session.commit()
            flash("成功发送")
            redirect(url_for('message.index'))
    return redirect(url_for('message.index'))
        