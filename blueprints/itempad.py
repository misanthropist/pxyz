from flask import Blueprint, render_template, current_app, session, request, flash, redirect, url_for
from pxyz.models import Item, User, Comment, Collect, Message
from pxyz.extensions import db
from pxyz.decorators import login_require, permission_required

itempad_bp = Blueprint('itempad', __name__)

@itempad_bp.route('/')
@itempad_bp.route('/itempad/<int:page>/')
def index(page=1):
    user = User.query.filter_by(username=session.get('login_user')).first()
    if user and user.is_admin:
        pagination = Item.query.order_by(Item.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
    else:
        pagination = Item.query.filter_by(deleted=False).order_by(Item.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])

    return render_template('itempad/index.html', pagination=pagination, user=user)
 
@itempad_bp.route('/itempad/search/')
@itempad_bp.route('/itempad/search/<int:page>/')
def search(page=1, kw=None):
    kw = request.args.get('kw', session.get('kw'))
    if kw:
        session['kw'] = kw
        username = session.get('login_user')
        user = User.query.filter_by(username=username).first()
        if kw[:4] == 'tag_':
            pagination = Item.query.filter(Item.item_type==kw[4:]).order_by(Item.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
        elif kw[:5] == "user_":
            user_id = kw[5:]
            pagination = user.items.order_by(Item.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
        elif kw[:8] == "collect_":
            user_id = kw[8:]
            pagination = Item.query.join(Collect).join(User).filter(User.id==user_id).order_by(Collect.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
        elif kw[:8] == "comment_":
            user_id = kw[8:]
            pagination = Item.query.join(Comment).join(User).filter(User.id==user_id).order_by(Comment.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
        else:
            pagination = Item.query.filter(Item.title.like('%{}%'.format(kw))).order_by(Item.timestamp.desc()).paginate(page=page, per_page=current_app.config['PXYZ_ITEM_PER_PAGE'])
        return render_template('itempad/search.html', pagination=pagination, user=user)
    else:
        return redirect(url_for('itempad.index'))

@itempad_bp.route('/item/<int:item_id>/')
def content(item_id=None):
    if item_id:
        item = Item.query.filter(Item.id==item_id).first()
        username = session.get('login_user')
        user = User.query.filter_by(username=username).first()
        url = "itempad/{}.html".format(item.item_type)
        return render_template(url, item=item, user=user)
    else:
        return redirect(url_for('itempad.index'))


@itempad_bp.route('/item/<int:item_id>/collect', methods=['POST'])
@login_require
@permission_required('COLLECT')
def collect(item_id):
    item = Item.query.get(item_id)
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first() 
    if user.is_collecting(item):
        flash('已经收藏过')
        return redirect(url_for('itempad.content', item_id=item.id))
    else:
        user.collect(item)
        db.session.commit()
        flash('成功收藏')
        return redirect(url_for('itempad.content', item_id=item.id))

@itempad_bp.route('/item/<int:item_id>/uncollect', methods=['POST'])
@login_require
@permission_required('COLLECT')
def uncollect(item_id):
    item = Item.query.get(item_id)
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first() 
    if not user.is_collecting(item):
        flash('还未收藏过')
        return redirect(url_for('itempad.content', item_id=item.id))
    else:
        user.uncollect(item)
        db.session.commit()
        flash('成功取消收藏')
        return redirect(url_for('itempad.content', item_id=item.id))

@itempad_bp.route('/item/<int:item_id>/new_comment', methods=['POST'])
@login_require
@permission_required('COMMENT')
def new_comment(item_id):
    username = session.get('login_user')
    user = User.query.filter_by(username=username).first()
    item = Item.query.get(item_id)
    if request.form:
        comment_body = request.form.get('new_comment')
        comment = Comment(
            content = comment_body,
            commenter_id = user.id,
            item_id = item.id
        )
        db.session.add(comment)
        flash('成功评论')
        message = ' <a href="{}">{}</a> 评论了 <a href="{}">{}</a> '.format(url_for('user.index', user_id=user.id), user.username, url_for('itempad.content', item_id=item_id), item.title)
        Message.push_message(user, item.uploader, message)
        db.session.commit()
    return redirect(url_for('itempad.content', item_id=item_id))

@itempad_bp.route('/item/<int:item_id>/delete_comment', methods=['POST'])
@login_require
@permission_required('MANAGE')
def delete_comment(item_id):
    if request.form:
        comment_id = request.form.get('comment_id')
        comment = Comment.query.get(comment_id)
        db.session.delete(comment)
        db.session.commit()
        flash('成功删除评论')
    return redirect(url_for('itempad.content', item_id=item_id))


@itempad_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_require
@permission_required('MANAGE')
def delete_item(item_id):
    item = Item.query.get(item_id)
    item.deleted = True
    db.session.commit()
    flash('成功回收 {}'.format(item.title))
    return redirect(request.referrer)

@itempad_bp.route('/item/<int:item_id>/restore', methods=['POST'])
@login_require
@permission_required('MANAGE')
def restore(item_id):
    item = Item.query.get(item_id)
    item.deleted = False
    db.session.commit()
    flash('成功恢复 {}'.format(item.title))
    return redirect(request.referrer)