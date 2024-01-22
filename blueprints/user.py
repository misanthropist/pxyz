from flask import Blueprint, render_template, redirect, url_for, session, flash, request, current_app
from pxyz.decorators import login_require, permission_required
from pxyz.extensions import db
from pxyz.models import User, Message, Follow

user_bp = Blueprint('user', __name__)


@user_bp.route('/user/login', methods=['GET', 'POST'])
def login():
    user_name = session.get('login_user')
    user = User.query.filter_by(username=user_name).first()
    if user:
        return redirect(url_for('user.index'))
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('请先注册')
            return redirect(url_for('user.register'))
        elif not user.validate_password(password):
            flash('密码错误')
            return redirect(url_for('user.login'))
        else:
            session['login_user'] = username
            return redirect(url_for('user.index'))
    return render_template('user/login.html', user=user)


@user_bp.route('/logout')
@login_require
def logout():
    session.pop('login_user', None)
    return redirect(url_for('itempad.index'))

@user_bp.route('/user/register', methods=['GET', 'POST'])
def register():
    if request.form:
        username = request.form.get('username')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        if User.query.filter_by(username=username).first():
            flash("用户名已经存在")
            return redirect(url_for('user.register'))
        elif password == password2:
            User.add_user(username, password)
            db.session.commit()
            flash("成功注册")
            return redirect(url_for('user.login'))
        else:
            flash("两次密码不相同")
            return redirect(url_for("user.register"))
    return render_template('user/register.html', user=None)

@user_bp.route('/user/')
@user_bp.route('/user/<int:user_id>/')
@login_require
def index(user_id=None):
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    if user_id:
        other = User.query.get(user_id)
        return render_template('user/index.html', user=user, other=other)
    else:
        return render_template('user/index.html', user=user, other=user)

@user_bp.route('/user/<int:user_id>/follow', methods=['POST'])
@login_require
@permission_required('FOLLOW')
def follow(user_id):
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    other = User.query.get(user_id)
    if user.is_following(other):
        flash('已经关注')
        return redirect(url_for('user.index', user_id=user_id))
    user.follow(other)
    message = ' <a href="{}">{}</a> 关注了 <a href="{}">{}</a> '.format(url_for('user.index', user_id=user.id), user.username,url_for('user.index', user_id=other.id), other.username)
    Message.push_message(user, other, message)
    db.session.commit()
    flash('成功关注')
    return redirect(url_for('user.index', user_id=user_id))

@user_bp.route('/user/<int:user_id>/unfollow', methods=['POST'])
@login_require
def unfollow(user_id):
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    other = User.query.get(user_id)
    if not user.is_following(other):
        flash('还未关注')
        return redirect(url_for('user.index', user_id=user_id))
    user.unfollow(other)
    message = ' <a href="{}">{}</a> 取消关注了 <a href="{} ">{}</a>'.format(url_for('user.index', user_id=user.id), user.username,url_for('user.index', user_id=other.id), other.username)
    Message.push_message(user, other, message)
    db.session.commit()
    flash('成功取消关注')
    return redirect(url_for('user.index', user_id=user_id))

@user_bp.route('/userpad/')
@user_bp.route('/userpad/<int:page>/')
@login_require
def userpad(page=1):
    user = User.query.filter_by(username=session.get('login_user')).first()
    pagination = User.query.order_by(User.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_USER_PER_PAGE'])
    return render_template("user/userpad.html", pagination=pagination, user=user)

@user_bp.route('/userpad/search')
@user_bp.route('/userpad/search/<int:page>/')
@login_require
def search(page=1, ukw=None):
    ukw = request.args.get('ukw', session.get('kw'))
    user = User.query.filter_by(username=session.get('login_user')).first()
    if ukw:
        session['ukw'] = ukw
        username = session.get('login_user')
        user = User.query.filter_by(username=username).first()
        if ukw[:7] == 'follow_':
            pagination = User.query.join(Follow, User.id==Follow.follow_id).filter(Follow.followed_id==user.id).order_by(User.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_USER_PER_PAGE'])
        elif ukw[:9] == 'followed_':
            pagination = User.query.join(Follow, User.id==Follow.followed_id).filter(Follow.follow_id==user.id).order_by(User.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_USER_PER_PAGE'])
        else:
            pagination = User.query.filter(User.username.like('%{}%'.format(ukw))).order_by(User.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_USER_PER_PAGE'])
        return render_template('user/search.html', pagination=pagination, user=user)
    else:
        return redirect(url_for('user.userpad'))

@user_bp.route('/user/<int:user_id>/lock', methods=['POST'])
@login_require
@permission_required('MANAGE')
def lock(user_id):
    user = User.query.get(user_id)
    user.lock()
    db.session.commit()
    flash('成功锁定 {}'.format(user.username))
    return redirect(request.referrer)

@user_bp.route('/user/<int:user_id>/unlock', methods=['POST'])
@login_require
@permission_required('MANAGE')
def unlock(user_id):
    user = User.query.get(user_id)
    user.unlock()
    db.session.commit()
    flash('成功解锁 {}'.format(user.username))
    return redirect(request.referrer)
