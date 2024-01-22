# pxyz

内容分享社交网站，游客可以自由浏览文本、图书、图片、音乐、视频，注册用户可以发布、评论、收藏这些内容，还可以关注用户、向他人发消息等。

## 1 运行环境

### 1.1 核心环境

Flask框架提供了最基础的请求响应处理网关和模板引擎。

Flask：Flask是一个轻量级的WSGI网页应用框架。它易于使用和学习，并能制作出复杂的应用。它本质是一个Werkzeug和Jinja2的包装器。

click：命令行工具。

Werkzeug：WSGI工具集。

itsdangerous：加密签名功能。

Jinja2：模板渲染引擎。

MarkupSafe：HTML字符转义工具。

### 1.2 扩展环境

包括数据库、文件监视等相关的库。

Flask-SQLAlchemy：在Flask中简化操作数据库。

SQLAlchemy：ORM工具。

greenlet：轻量级协程库。

## 2 MVC架构

在MVC架构中，程序被分为三个组件：数据处理(Model)、用户界面(View)、交互逻辑(Controller)。

### 2.1 数据处理

所有的数据表分成三大类。第一大类权限控制信息，包括角色数据表、权限数据表。

```sql
CREATE TABLE roles_permissions (
    role_id INTEGER, 
    permission_id INTEGER, 
    FOREIGN KEY(role_id) REFERENCES role (id), 
    FOREIGN KEY(permission_id) REFERENCES permission (id)
)
CREATE TABLE role (
    id INTEGER NOT NULL, 
    name VARCHAR(64), 
    PRIMARY KEY (id), 
    UNIQUE (name)
)
CREATE TABLE permission (
    id INTEGER NOT NULL, 
    name VARCHAR(64), 
    PRIMARY KEY (id), 
    UNIQUE (name)
)
```

第二大类是用户信息，包括用户本身情况的数据表、关注数据表、通知数据表。

```sql
CREATE TABLE user (
    id INTEGER NOT NULL, 
    username VARCHAR(16), 
    password_hash VARCHAR(128), 
    cover_url VARCHAR(256), 
    deleted BOOLEAN, 
    timestamp DATETIME, 
    role_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(role_id) REFERENCES role (id)
)
CREATE TABLE follow (
    id INTEGER NOT NULL, 
    timestamp DATETIME, 
    follow_id INTEGER, 
    followed_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(follow_id) REFERENCES user (id), 
    FOREIGN KEY(followed_id) REFERENCES user (id)
)
CREATE TABLE message (
    id INTEGER NOT NULL, 
    content TEXT NOT NULL, 
    is_read BOOLEAN, 
    timestamp DATETIME, 
    receiver_id INTEGER, 
    sender_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(receiver_id) REFERENCES user (id), 
    FOREIGN KEY(sender_id) REFERENCES user (id)
)
```

第三大类是文本、图书、图片、音乐、视频这些物品信息，包括物品本身情况的数据表、评论数据表、收藏数据表。

```sql
CREATE TABLE item (
    id INTEGER NOT NULL, 
    title VARCHAR(256), 
    file_url VARCHAR(256), 
    cover_url VARCHAR(256), 
    item_type VARCHAR(16), 
    deleted BOOLEAN, 
    timestamp DATETIME, 
    uploader_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(uploader_id) REFERENCES user (id)
)
CREATE TABLE comment (
    id INTEGER NOT NULL, 
    content TEXT, 
    timestamp DATETIME, 
    item_id INTEGER, 
    commenter_id INTEGER, 
    PRIMARY KEY (id), 
    FOREIGN KEY(item_id) REFERENCES item (id), 
    FOREIGN KEY(commenter_id) REFERENCES user (id)
)
CREATE TABLE collect (
    timestamp DATETIME, 
    collector_id INTEGER NOT NULL, 
    collected_id INTEGER NOT NULL, 
    PRIMARY KEY (collector_id, collected_id), 
    FOREIGN KEY(collector_id) REFERENCES user (id), 
    FOREIGN KEY(collected_id) REFERENCES item (id)
)
```

### 2.2 网页模板

物品展示类的网页模板，按其展示内容不同采用不同的模板来展示。
文本：分章节展示。
图书：采用jquery.js、jszip.js、epub.js库来打开电子书。
图片：直接采用img元素显示
音频：直接采用audio元素显示。
视频：直接采用video元素显示。

### 2.3 路由控制

所有URL端点分为四大类。

第一大类是物品类的端点，包括三个展示页面和六个操作功能。

```python
#获取所有物品
@itempad_bp.route('/')
@itempad_bp.route('/itempad/<int:page>/')
def index(page=1):
    pass

#获取物品搜索结果
@itempad_bp.route('/itempad/search/')
@itempad_bp.route('/itempad/search/<int:page>/')
def search(page=1, kw=None):
    pass

#物品详情
@itempad_bp.route('/item/<int:item_id>/')
def content(item_id=None):
    pass

#收藏物品
@itempad_bp.route('/item/<int:item_id>/collect', methods=['POST'])
@login_require
@permission_required('COLLECT')
def collect(item_id):
    pass

#取消收藏
@itempad_bp.route('/item/<int:item_id>/uncollect', methods=['POST'])
@login_require
@permission_required('COLLECT')
def uncollect(item_id):
    pass

#评论物品
@itempad_bp.route('/item/<int:item_id>/new_comment', methods=['POST'])
@login_require
@permission_required('COMMENT')
def new_comment(item_id):

#删除评论
@itempad_bp.route('/item/<int:item_id>/delete_comment', methods=['POST'])
@login_require
@permission_required('MANAGE')
def delete_comment(item_id):
    pass

#回收物品
@itempad_bp.route('/item/<int:item_id>/delete', methods=['POST'])
@login_require
@permission_required('MANAGE')
def delete_item(item_id):
    pass

#恢复物品
@itempad_bp.route('/item/<int:item_id>/restore', methods=['POST'])
@login_require
@permission_required('MANAGE')
def restore(item_id):
    pass
```

第二大类是用户类的端点，包括五个展示页面和五个操作功能。

```python
#获取所有用户
@user_bp.route('/userpad/')
@user_bp.route('/userpad/<int:page>/')
@login_require
def userpad(page=1):
    pass

#获取用户搜素结果
@user_bp.route('/userpad/search')
@user_bp.route('/userpad/search/<int:page>/')
@login_require
def search(page=1, kw=None);
    pass

#用户详情
@user_bp.route('/user/')
@user_bp.route('/user/<int:user_id>/')
@login_require
def index(user_id=None):
    pass

#注册
@user_bp.route('/user/register', methods=['GET', 'POST'])
def register():
    pass

#登录
@user_bp.route('/user/login', methods=['GET', 'POST'])
def login():
    pass

#退出
@user_bp.route('/logout')
@login_require
def logout():
    pass

#关注
@user_bp.route('/user/<int:user_id>/follow', methods=['POST'])
@login_require
@permission_required('FOLLOW')
def follow(user_id):
    pass

#取消关注
@user_bp.route('/user/<int:user_id>/unfollow', methods=['POST'])
@login_require
def unfollow(user_id):
    pass

#锁定
@user_bp.route('/user/<int:user_id>/lock', methods=['POST'])
@login_require
@permission_required('MANAGE')
def lock(user_id):
    pass

#解锁
@user_bp.route('/user/<int:user_id>/unlock', methods=['POST'])
@login_require
@permission_required('MANAGE')
def unlock(user_id):
    pass
```

第三大类是上传文件类的端点。

```python
#获取文件路径
@upload_bp.route('/upload/<path:filename>')
def get_file(filename):
    pass

#上传文件
@upload_bp.route('/upload/', methods=['GET', 'POST'])
@login_require
@permission_required('UPLOAD')
def index():
    pass
```

第四大类是消息通知类的端点。

```python
#展示消息
@message_bp.route('/message/')
@message_bp.route('/message/<int:page>/')
@login_require
def index(page=1):
    pass

#发送消息
@message_bp.route('/message/', methods=['POST'])
@message_bp.route('/message/<int:page>/', methods=['POST'])
@login_require
def send():
    pass
```

## 3 部署

一般需要购买域名、VPS来部署代码，运行网站程序，而这里为了简单省事，采用了其他方法，一种部署到本地，一种部署到免费的pythonanywhere平台。

### 3.1 本地

用gunicorn作为应用接口网关，nginx代理静态资源。

编辑nginx.conf文件如下：

```nginx
http {
    client_max_body_size 300m;
    server {
        listen 5001;
        server_name _;

        #proxy_set_header X_Forwarded_Host $host;
        #proxy_set_header X_Forwarded_Server $host;
        #proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header REMOTE-HOST $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_redirect off;

            proxy_set_header Host $host:5001;
        }

        location /static {
            alias /data/data/com.termux/files/home/temp/pxyz/pxyz/static/;
            expires 30d;
        }

        location /upload_file {
            alias /data/data/com.termux/files/home/temp/pxyz/temp/upload_test/;
            expires 30d;
        }
    }
}
```

编辑wsgi.py文件如下：

```python
from pxyz import create_app
app = create_app('testing')
```

启动服务器：

```bash
nginx
nohup gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app &
```

### 3.2 pythonanywhere平台

编辑wsgi.py文件如下：

```python
import sys
path = '/home/doudouwang/misanthropist.github.io'
if path not in sys.path:
    sys.path.append(path)

from pxyz import create_app
app = create_app()
application = app
```
