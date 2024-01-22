import os
from flask import Blueprint, render_template, request, url_for, current_app, flash, redirect, session, send_from_directory
from pxyz.extensions import db
from pxyz.decorators import login_require, permission_required
from pxyz.models import User, Item

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload/<path:filename>')
def get_file(filename):
    upload_path = current_app.config['PXYZ_UPLOAD_PATH']
    return send_from_directory(upload_path, filename)

@upload_bp.route('/upload/', methods=['GET', 'POST'])
@login_require
@permission_required('UPLOAD')
def index():
    upload_path = current_app.config['PXYZ_UPLOAD_PATH']
    max_f_size = current_app.config['PXYZ_MAX_FILE_SIZE']
    max_cover_size = current_app.config['PXYZ_MAX_COVER_SIZE']
    user_name = session.get('login_user')
    user = User.query.filter_by(username=user_name).first()
    if request.files:
        single_file = ['txt', 'epub', 'jpg', 'mp3', 'mp4']
        for tag in single_file:
            f = request.files.get(tag, None)
            f_cover = request.files.get(tag+'_cover', None)
            f_title = request.form.get(tag+'_title', None)
            if f and f_cover and f_title:
                title = f_title
                item = Item.query.filter_by(title=title).first()
                if item:
                    flash("{} 已存在".format(item.title))
                else:
                    f.seek(0, os.SEEK_END)
                    f_size = f.tell()
                    f.seek(0)
                    f_cover.seek(0, os.SEEK_END)
                    f_cover_size = f_cover.tell()
                    f_cover.seek(0)
                    if f_size > max_f_size or f_cover_size > max_cover_size:
                        flash("{}大小超出限制，上传文件{}M，最大为{}M，上传封面{}K，最大为{}K".format(title, f_size/1024/1024, max_f_size/1024/1024, f_cover_size/1024, max_cover_size/1024))
                    else:
                        file_url = os.path.join('/upload', tag, title+'.'+tag)
                        f.save(os.path.join(upload_path, tag, title+'.'+tag))
                        f_cover.save(os.path.join(upload_path, 'cover', title+'.jpg'))
                        cover_url = os.path.join('/upload/cover', title+'.jpg')
                        Item.add_item(title, file_url, cover_url, tag, user.username)
                        flash("成功上传 {}".format(title))
               
        db.session.commit()
        return redirect(url_for('itempad.index'))
    return render_template('upload/index.html')
