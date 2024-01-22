import os
import glob
import click
from pxyz.models import Item, User, Role

admin = os.getenv('PXYZ_ADMIN', "admin")
password = os.getenv('PXYZ_ADMIN_PASSWORD', 'helloadmin')

test_user = os.getenv('PXYZ_USER', "test_user")
user_password = os.getenv('PXYZ_USER_PASSWORD', 'hellouser')

test_locked = os.getenv('PXYZ_LOCKED', "test_locked")
locked_password = os.getenv('PXYZ_LOCKED_PASSWORD', 'hellolocked')

roles_permissions_map = {
    'Locked': ['FOLLOW', 'COLLECT'],
    'User': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD'],
    'Admin': ['FOLLOW', 'COLLECT', 'COMMENT', 'UPLOAD', 'MANAGE']
}
item_types = ['epub', 'jpg', 'mp3', 'mp4', 'txt']

def add_upload_item(upload_dir, item_type, username):
    item_paths = glob.glob(os.path.join(upload_dir, item_type, '*.'+item_type))
    titles = [os.path.basename(f).split('.')[0] for f in item_paths]
    file_urls = ["/upload/{}/{}.{}".format(item_type, title, item_type) for title in titles]
    cover_urls = ["/upload/cover/{}.jpg".format(title) for title in titles]
    for item in zip(titles, file_urls, cover_urls):
        Item.add_item(item[0], item[1], item[2], item_type, username)
    click.echo('add '+item_type)

def gen_all(app):
    upload_dir = app.config['PXYZ_UPLOAD_PATH']

    click.echo('add the roles and permissions')
    Role.add_roles(roles_permissions_map)

    click.echo('add users')
    User.add_user(admin, password, "/upload/cover/admin.jpg", 'Admin')
    User.add_user(test_user, user_password, "/upload/cover/admin.jpg", 'User')
    User.add_user(test_locked, locked_password, '/upload/cover/admin.jpg', 'Locked')
    
    click.echo('add item')
    for item_type in item_types:
        add_upload_item(upload_dir, item_type, "admin")



