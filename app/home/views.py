from . import home
from flask import render_template, redirect, url_for, session, flash, request, Response
from app.models import Item, User, Comment, Tag, UserLog, Collect
from app import db, rd
from app.home.forms import LoginForm, RegisterForm, UserDetailForm, PwdForm, CommentForm, TagForm, UserForm, ItemForm
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from werkzeug.utils import secure_filename
import os, datetime, uuid, json, time, stat

USER_IMAGE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/user/')
ITEM_IMAGE = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../static/item/')

def change_filename(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.datetime.now().strftime("%Y%m%d%H%M%S") + str(uuid.uuid4().hex + fileinfo[-1])
    return filename

def user_login_require(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('login_user', None) is None:
            return redirect(url_for('home.login', next=request.url))
        return func(*args, **kwargs)
    return decorated_function

def root_login_require(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if session.get('login_star', None) < 99:
            return redirect(url_for('home.index'))
        return func(*args, **kwargs)
    return decorated_function

@home.route('/')
@home.route("/<int:page>/", methods=['GET', 'POST'])
def index(page=1):
    if not page:
        page = 1
    if session.get('login_star', None) == 99:
        items = Item.query.order_by(Item.id.desc()).paginate(page=page, per_page=12) 
    else:
        items = Item.query.filter(Item.score<=1).order_by(Item.id.desc()).paginate(page=page, per_page=12)
    return render_template('home/index.html', items=items)

@home.route("/login/", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        data = form.data
        login_user = User.query.filter_by(name=data['account']).first()
        if not login_user:
            flash('用户不存在')
            return redirect(url_for('home.login', next=request.args.get('next')))
        elif not check_password_hash(login_user.pwd, data['pwd']):
            flash('密码错误')
            return redirect(url_for('home.login', next=request.args.get('next')))
        user_log = UserLog(
            ip = request.remote_addr,
            user = login_user
        )
        db.session.add(user_log)
        db.session.commit()
        session['login_name'] = login_user.name
        session['login_face'] = login_user.face
        session['login_user'] = login_user.id
        session['login_star'] = login_user.star
        return redirect(request.args.get('next') or url_for('home.index'))

    return render_template('home/login.html', form=form)

@home.route("/logout/")
def logout():
    session.pop('login_user', None)
    session.pop('login_star', None)
    session.pop('login_face', None)
    session.pop('login_name', None)
    return redirect(url_for('home.login'))

@home.route("/register/", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = form.data
        if User.query.filter_by(name=data['name']).count() == 1:
            flash('昵称已经存在', category='danger')
            return redirect(url_for('home.register'))
        elif User.query.filter_by(email=data['email']).count() == 1:
            flash("邮箱已经存在", category='danger')
            return redirect(url_for('home.register'))
        elif User.query.filter_by(phone=data['phone']).count() == 1:
            flash("手机已经存在", category='danger')
            return redirect(url_for('home.register'))
        elif User.query.filter_by(qq=data['qq']).count() == 1:
            flash("qq已经存在", category='danger')
            return redirect(url_for('home.register'))
        user = User(
            name=data['name'],
            pwd=generate_password_hash(data['pwd']),
            email=data['email'],
            phone=data['phone'],
            qq=data['qq']
        )
        user_log = UserLog(
            ip = request.remote_addr,
            user = user
        )
        db.session.add(user_log)
        db.session.add(user)
        db.session.commit()
        flash('注册成功, 请登录', category='success')
        return redirect(url_for('home.login'))

    return render_template('home/register.html', form=form)


@home.route('/user/', methods=['GET', 'POST'])
@user_login_require
def user():
    login_user = User.query.get(session['login_user'])
    form = UserDetailForm(
        name=login_user.name,
        email=login_user.email,
        phone=login_user.phone,
        info=login_user.info
    )
    if form.validate_on_submit():
        data = form.data
        face_save_path = USER_IMAGE
        if not os.path.exists(face_save_path):
            os.makedirs(face_save_path)  # 如果文件保存路径不存在，则创建一个多级目录
            os.chmod(face_save_path, stat.S_IRWXU)  # 授予可读写权限

        if form.face.data:
            # 上传文件不为空保存
            if login_user.face and os.path.exists(os.path.join(face_save_path, login_user.face)):
                os.remove(os.path.join(face_save_path, login_user.face))
            # 获取上传文件名称
            # file_face = secure_filename(form.face.data.filename)
            # !!!AttributeError: 'str' object has no attribute 'filename'，前端需要加上enctype="multipart/form-data"
            login_user.face = change_filename(form.face.data.filename)
            form.face.data.save(face_save_path + login_user.face)

        if login_user.name != data['name'] and User.query.filter_by(name=data['name']).count() == 1:
            flash('昵称已经存在', 'danger')
            return redirect(url_for('home.user'))
        login_user.name = data['name']

        if login_user.email != data['email'] and User.query.filter_by(email=data['email']).count() == 1:
            flash('邮箱已经存在', 'danger')
            return redirect(url_for('home.user'))
        login_user.email = data['email']

        if login_user.phone != data['phone'] and User.query.filter_by(phone=data['phone']).count() == 1:
            flash('手机号已经存在', 'danger')
            return redirect(url_for('home.user'))
        login_user.phone = data['phone']

        login_user.info = data['info']

        db.session.commit()
        flash('修改资料成功', 'success')
        return redirect(url_for('home.user'))
    return render_template('home/user.html', form=form, login_user=login_user)

@home.route("/pwd/", methods=['GET', 'POST'])
@user_login_require
def pwd():
    login_user = User.query.get(int(session['login_user']))
    form = PwdForm()
    if form.validate_on_submit():
        data = form.data
        if check_password_hash(login_user.pwd, data['oldpwd']):
            login_user.pwd = generate_password_hash(data['newpwd'])
            db.session.commit()
            flash('密码修改成功，请重新登录', category='success')
            return redirect(url_for('home.login'))
        else:
            flash('旧密码不正确', category='danger')
            return redirect(url_for('home.pwd'))
    return render_template('home/pwd.html', form=form)

@home.route("/tag/<int:page>/", methods=['GET', 'POST'])
@root_login_require
def tag(page=None, op='list'):
    if page == None:
        page = 1
    form = TagForm()
    page_tags = Tag.query.order_by(Tag.add_time.desc()).paginate(page=page, per_page=3)
    if request.method == 'POST':
        op = request.args.get('op')
        if op == 'del':
            del_id = request.args.get('tag_id')
            tag = Tag.query.get(del_id)
            db.session.delete(tag)
            db.session.commit()
            flash('成功删除标签', category='success')
            return redirect(url_for('home.tag', page=1))
        if op == 'update':
            form.id = update_id = request.args.get('tag_id')
            tag = Tag.query.get(update_id)
            form.name.render_kw.update(value=tag.name)
            return render_template('home/tag.html', form=form, page_tags=page_tags, op=op)
        if op == 'updated':
            if form.validate_on_submit():
                form.id = update_id = request.args.get('tag_id')
                tag = Tag.query.get(update_id)
                data = form.data
                if Tag.query.filter_by(name=data['name']).count():
                    flash('标签已存在！', category="danger")
                    # return redirect(url_for('home.tag', page=1, op='update', tag_id=tag.id))
                    return render_template('home/tag.html', form=form, page_tags=page_tags, op='update', tag_id=tag.id)
                tag.name = data['name']
                form.name.render_kw.update(value='')
                db.session.commit()
                flash('标签修改成功！', category='success')
                return redirect(url_for('home.tag', page=1))
        if op == 'add':
            if form.validate_on_submit():
                data = form.data
                if Tag.query.filter_by(name=data['name']).count():
                    flash('标签已存在！', category="danger")
                    return redirect(url_for('home.tag', pages=1))
                tag = Tag(
                    name=data['name']
                )
                db.session.add(tag)
                db.session.commit()
                flash('标签添加成功！', category='success')
                return redirect(url_for('home.tag', page=1))
    return render_template('home/tag.html', form=form, page_tags=page_tags, op=op)

@home.route("/comment/<int:page>", methods=['GET','POST'])
@user_login_require
def comment(page):
    if request.method == 'POST':
        op = request.args.get('op')
        comment_id = request.args.get('comment_id')
        comment = Comment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('成功删除评论', category='success')
        return redirect(url_for('home.comment',page=1))
    page_comments = Comment.query.join(
        Item
    ).join(
        User
    ).filter(
        Item.id == Comment.item_id,
        User.id == session['login_user']
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page, per_page=10)
    return render_template("home/comment.html", page=1, page_comments=page_comments)

@home.route("/userlog/<int:page>")
@user_login_require
def userlog(page):
    page_userlog = UserLog.query.filter_by(user_id=session['login_user']).paginate(page=page, per_page=10)

    return render_template("home/userlog.html", page=1, page_userlog=page_userlog)

@home.route("/collect/<int:page>", methods=['GET','POST'])
@user_login_require
def collect(page):
    page_collects = Collect.query.order_by(Collect.add_time.desc()).paginate(page=page, per_page=10)
    if request.args.get('op') == 'delete':
        collect = Collect.query.get(request.args.get('collect_id'))
        collect.item.collect_num -= 1
        db.session.delete(collect)
        db.session.commit()
        flash('成功删除收藏', category='success')
        return redirect(url_for('home.collect', page=1))
    return render_template("home/collect.html", page=1, page_collects=page_collects)

@home.route("/search/", methods=['GET', 'POST'])
def search():
    keyword = request.args.get('keyword', '')
    search_items = Item.query.filter(
        Item.title.ilike("%" + keyword + "%")
    ).order_by(
        Item.add_time.desc()
    )
    search_count = search_items.count()
    return render_template('home/search.html', keyword=keyword, search_items=search_items, search_count=search_count)

@home.route("/play/<int:item_id>/page/<int:page>", methods=['GET', 'POST'])
def play(item_id=None, page=None):
    item = Item.query.filter(Item.id==item_id).first()
    
    if request.method == 'GET' and page == 1:
        if not item.click_num:
            item.click_num = 0
        item.click_num += 1
        db.session.commit()

    form = CommentForm()
    if 'login_user' not in session:
        form.submit.render_kw = {
            'disabled': "disabled",
            "class": "btn btn-outline-success"
        }
    if 'login_user' in session:
        op = request.args.get('op')
        if form.validate_on_submit() and op == "add_comment":
            data = form.data
            comment = Comment(
                content=data['content'],
                item_id=item.id,
                user_id=session['login_user']
            )
            db.session.add(comment)
            if not item.comment_num:
                item.comment_num = 0
            item.comment_num += 1
            db.session.commit()
            flash('评论成功', category='success')
            return redirect(url_for('home.play', item_id=item.id, page=1))
        if op == "add_collect":
            collected = Collect.query.join(
                Item
            ).join(
                User
            ).filter(
                Item.id == item.id,
                User.id == session['login_user']
            )
            if collected.count():
                flash('已收藏过', category='danger')
                return redirect(url_for('home.play', item_id=item.id, page=1))
            else:
                collect = Collect(
                    item_id=item.id,
                    user_id=session['login_user']
                )
                db.session.add(collect)
                if not item.collect_num:
                    item.collect_num=0
                item.collect_num += 1
                db.session.commit()
                flash('收藏成功', category='success')
                return redirect(url_for('home.play', item_id=item.id, page=1))
    
    if page is None:
        page = 1
    page_comments = Comment.query.join(
        Item
    ).join(
        User
    ).filter(
        Item.id == item.id, 
        User.id == Comment.user_id
    ).order_by(
        Comment.add_time.desc()
    ).paginate(page=page, per_page=10)
    return render_template("home/play.html", item=item, form=form, page_comments=page_comments)

@home.route("/tm/v3/", methods=["GET", "POST"])
def tm():
    resp = ''
    if request.method == "GET":
        item_id = request.args.get('id')
        key = item_id
        if rd.llen(key):
            msgs = rd.lrange(key, 0, 2999)
            tm_data = []
            for msg in msgs:
                msg = json.loads(msg)
                tmp_data = [msg['time'], msg['type'], msg['color'], msg['author'], msg['text']]
                tm_data.append(tmp_data)
            res = {
                "code": 0,
                "data": tm_data,
            }
        else:
            print('Redis中暂无内容')
            res = {
                "code": 1,
                "data": []
            }
        resp = json.dumps(res)

    if request.method == "POST":  # 添加弹幕
        data = json.loads(request.get_data())
        # print(data)
        msg = {
            "__v": 0,
            "author": data["author"],
            "time": data["time"],  # 发送弹幕视频播放进度时间
            "date": int(time.time()),  # 当前时间戳
            "text": data["text"],  # 弹幕内容
            "color": data["color"],  # 弹幕颜色
            "type": data['type'],  # 弹幕位置
            "ip": request.remote_addr,
            "_id": datetime.datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex,
            "player": data['id']
        }
        res = {
            "code": 0,
            "data": msg
        }
        resp = json.dumps(res)
        rd.lpush(data['id'], json.dumps(msg))  # 将添加的弹幕推入redis的队列中
    return Response(resp, mimetype='application/json')


@home.route('/userplus/<int:page>')
@root_login_require
def userplus(page):
    page_users = User.query.paginate(page=page, per_page=10)
    return render_template('home/userplus.html', page_users=page_users)

@home.route('/item/<int:page>', methods=['GET', 'POST'])
@root_login_require
def item(page, op='list'):
    form = ItemForm()
    page_items = Item.query.order_by(Item.add_time.desc()).paginate(page=page, per_page=10)
    if request.method == 'POST':
        op = request.args.get('op')
        if op == 'delete':
            del_id = request.args.get('item_id')
            item = Item.query.get(del_id)
            if item.logo and os.path.exists(os.path.join(ITEM_IMAGE, item.logo)):
                os.remove(os.path.join(ITEM_IMAGE, item.logo))
            db.session.delete(item)
            db.session.commit()
            flash('成功删除作品', category='success')
            return redirect(url_for('home.item', page=1))
        if op == 'update':
            form.id = update_id = request.args.get('item_id')
            item = Item.query.get(update_id)
            form.title.render_kw.update(value=item.title)
            form.url.render_kw.update(value=item.url)
            # form.info=TextAreaField(u'desc', validators=[DataRequired()])
            form.logo_url=item.logo
            form.score.default = item.score
            form.tag_id.default = item.tag_id
            return render_template('home/item.html', form=form, page_items=page_items, op=op)
        if op == 'updated':
            if form.validate_on_submit():
                form.id = update_id = request.args.get('item_id')
                item = Item.query.get(update_id)
                data = form.data
                if Item.query.filter_by(title=data['title']).count() and item.title != data['title']:
                    flash('作品已存在！', category='danger')
                    return render_template('home/item.html', form=form, page_items=page_items, op='update', item_id=item.id)
                item.title = data['title']
                item.info = data['info']
                item.score = data['score']
                item.tag_id = data['tag_id']
                item.url = data['url']
                file_save_path = ITEM_IMAGE
                if not os.path.exists(file_save_path):
                    os.makedirs(file_save_path)
                    os.chmod(file_save_path, stat.S_IRWXU)
                if form.logo.data:
                    if item.logo and os.path.exists(os.path.join(file_save_path, item.logo)):
                        os.remove(os.path.join(file_save_path, item.logo))
                    # file_logo = secure_filename(form.logo.data.filename)
                    item.logo = change_filename(form.logo.data.filename)
                    form.logo.data.save(file_save_path + item.logo)
                db.session.merge(item)  # 调用merge方法，此时Movie实体状态并没有被持久化，但是数据库中的记录被更新了（暂时不明白）
                form.title.render_kw.update(value='')
                form.url.render_kw.update(value='')
                form.info.render_kw.update(value='')
                form.logo_url=''
                form.score.render_kw.update(value='')
                form.tag_id.render_kw.update(value='')
                db.session.commit()
                flash('修改电影成功', 'success')
                return redirect(url_for('home.item', page=1))
        if op == 'add':
            if form.validate_on_submit():
                data = form.data
                if Item.query.filter_by(title=data['title']).count():
                    flash('作品已存在！', category="danger")
                    return redirect(url_for('home.item', page=1))
                # file_url = secure_filename(form.url.data.filename)
                # file_logo = secure_filename(form.logo.data.filename)
                file_logo = form.logo.data.filename
                file_save_path = ITEM_IMAGE
                if not os.path.exists(file_save_path):
                    os.makedirs(file_save_path)
                    os.chmod(file_save_path, stat.S_IRWXU)
                logo = change_filename(file_logo)
                form.logo.data.save(file_save_path+logo)
                item = Item(
                    title=data['title'],
                    url=data['url'],
                    info=data['info'],
                    logo=logo,
                    score = data['score'],
                    tag_id=data['tag_id']
                )
                db.session.add(item)
                db.session.commit()
                flash('作品添加成功！', category='success')
                return redirect(url_for('home.item', page=1))
    return render_template('home/item.html', form=form, page_items=page_items, op=op)