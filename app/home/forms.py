from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FileField, SelectMultipleField
from wtforms.validators import DataRequired, EqualTo, Regexp, Length
from app.models import User, Tag 


class TagForm(FlaskForm):
    id = 0
    name = StringField(
        label="标签名称",
        validators=[
            DataRequired('请输入内容')
        ],
        description='标签名称',
        render_kw={
            'class': "form-control",
            'id': 'input_name',
            'placeholder': '请输入标签名称！'
        }
    )
    add = SubmitField(
        label='添加',
        render_kw={
            'class':'btn btn-outline-primary'
        }
    )
    delete = SubmitField(
        label="删除",
        render_kw={
            'class': 'btn-outline-success btn-sm'
        }
    )
    update = SubmitField(
        label="更新",
        render_kw={
            'class': 'btn-outline-success btn-sm'
        }
    )

class CommentForm(FlaskForm):
    content = TextAreaField(
        label='评论内容',
        validators=[
            DataRequired('请输入内容')
        ],
        description='内容',
        render_kw={
            # 'id': "input_content"
            'class': "form-control",
            'rows': "5"
        }
    )
    submit = SubmitField(
        label='提交评论',
        render_kw={
            "class": "btn btn-outline-success",
        }
    )

class PwdForm(FlaskForm):
    oldpwd = PasswordField(
        label='旧密码',
        validators=[
            DataRequired('请输入旧密码！')
        ],
        description='旧密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入旧密码",
            'required': "required"
        }
    )
    newpwd = PasswordField(
        label='新密码',
        validators=[
            DataRequired('请输入新密码！')
        ],
        description='新密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入新密码",
            'required': "required"
        }
    )
    repwd = PasswordField(
        label='重复密码',
        validators=[
            DataRequired('请输入重复密码！'),
            EqualTo('newpwd', message='两次密码不一致')
        ],
        description='重复密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入重复密码",
            'required': "required"
        }
    )
    submit = SubmitField(
        label='修改密码',
        render_kw={
            'class': "btn btn-success"
        }
    )

class UserDetailForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称！')
        ],
        description='昵称',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入昵称",
            'required': "required"
        }
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱！')
        ],
        description='邮箱',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入邮箱",
            'required': "required",
        }
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机！'),
            Regexp('^1[3|4|5|6|7|8][0-9]\d{4,8}$', message='手机格式不正确')
        ],
        description='手机',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入手机",
            'required': "required"
        }
    )
    face = FileField(
        label='头像',
        validators=[
            FileAllowed(['jpg', 'png'], '只能上传图片！'),
        ],
        description='头像',
    )
    info = TextAreaField(
        label='简介',
        validators=[
            DataRequired('请输入简介！')
        ],
        description='简介',
        render_kw={
            'required': False,
            'class': "form-control",
            'rows': "10",
        }
    )
    submit = SubmitField(
        label='保存',
        render_kw={
            'class': "btn btn-outline-success"
        }
    )

class RegisterForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称！'),
            Length(1,10, message="1-10个字符")
        ],
        description='昵称',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入昵称",
            'required': "required"
        }
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱！'),
            Regexp('^[A-Za-z0-9]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', message='邮箱格式不正确')
        ],
        description='邮箱',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入邮箱",
            'required': "required",
        }
    )
    qq = StringField(
        label='qq',
        validators=[
            DataRequired('请输入qq！')
        ],
        description='qq',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入qq',
            'required': 'required'
        }
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机！'),
            Regexp('^1[3|4|5|6|7|8][0-9]\d{4,8}$', message='手机格式不正确')
        ],
        description='手机',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入手机",
            'required': "required",
        }
    )
    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码！')
        ],
        description='密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入密码",
            'required': "required"
        }
    )
    repwd = PasswordField(
        label='重复密码',
        validators=[
            DataRequired('请输入重复密码！'),
            EqualTo('pwd', message='两次密码不一致')
        ],
        description='重复密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入重复密码",
            'required': "required"
        }
    )
    submit = SubmitField(
        label='注册',
        render_kw={
            'class': "btn btn-outline-success btn-block"
        }
    )

class LoginForm(FlaskForm):
    account = StringField(
        label='账号',
        validators=[
            DataRequired('请输入账号！')
        ],
        description='账号',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入账号",
            'required': "required"
        }
    )

    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired("请输入密码！")
        ],
        description='密码',
        render_kw={
            "class": "form-control",
            'placeholder': "请输入密码",
            "required": "required"
        }
    )

    submit = SubmitField(
        label='登录',
        render_kw={
            'class': 'btn btn-outline-primary btn-block'
        }
    )

class UserForm(FlaskForm):
    name = StringField(
        label='昵称',
        validators=[
            DataRequired('请输入昵称！'),
            Length(1,10, message="1-10个字符")
        ],
        description='昵称',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入昵称",
            'required': "required"
        }
    )
    pwd = PasswordField(
        label='密码',
        validators=[
            DataRequired('请输入密码！')
        ],
        description='密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入密码",
            'required': "required"
        }
    )
    repwd = PasswordField(
        label='重复密码',
        validators=[
            DataRequired('请输入重复密码！'),
            EqualTo('pwd', message='两次密码不一致')
        ],
        description='重复密码',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入重复密码",
            'required': "required"
        }
    )
    email = StringField(
        label='邮箱',
        validators=[
            DataRequired('请输入邮箱！'),
            Regexp('^[A-Za-z0-9]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', message='邮箱格式不正确')
        ],
        description='邮箱',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入邮箱",
            'required': "required",
        }
    )
    phone = StringField(
        label='手机',
        validators=[
            DataRequired('请输入手机！'),
            Regexp('^1[3|4|5|6|7|8][0-9]\d{4,8}$', message='手机格式不正确')
        ],
        description='手机',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入手机",
            'required': "required",
        }
    )
    qq = StringField(
        label='qq',
        validators=[
            DataRequired('请输入qq！')
        ],
        description='qq',
        render_kw={
            'class': 'form-control',
            'placeholder': '请输入qq',
            'required': 'required'
        }
    )
    face = FileField(
        label='头像',
        validators=[
            FileAllowed(['jpg', 'png'], '只能上传图片！'),
        ],
        description='头像',
    )
    info = TextAreaField(
        label='简介',
        validators=[
            DataRequired('请输入简介！')
        ],
        description='简介',
        render_kw={
            'required': False,
            'class': "form-control",
            'rows': "10",
        }
    )
    save = SubmitField(
        label='保存',
        render_kw={
            'class': "btn btn-outline-success"
        }
    )
    register = SubmitField(
        label='注册',
        render_kw={
            'class': "btn btn-outline-success btn-block"
        }
    )
    login = SubmitField(
        label='登录',
        render_kw={
            'class': 'btn btn-outline-primary btn-block'
        }
    )

class ItemForm(FlaskForm):
    id = 0
    title = StringField(
        label='名称',
        validators=[
            DataRequired('请输入作品名称！')
        ],
        description='作品名称',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入作品名称！"
        }
    )
    url = StringField(
        label='作品链接',
        validators=[
            DataRequired('请输入作品链接！')
        ],
        description='作品链接',
        render_kw={
            'class': "form-control",
            'placeholder': "请输入作品链接！"
        }
    )
    info = TextAreaField(
        label='简介',
        validators=[
            DataRequired('请输入简介！')
        ],
        description='简介',
        render_kw={
            'class': "form-control",
            'rows': "10",
        }
    )
    logo_src = ''
    logo = FileField(
        label='封面',
        validators=[
            DataRequired('请上传封面！')
        ],
        description='封面',
        render_kw={
            'class': "form-control"
        }
    )
    score = SelectField(
        default=1,
        label='评分',
        validators=[
            DataRequired('请选择评分！')
        ],
        description='评分',
        coerce=int,
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        render_kw={
            'class': "form-control"
        }
    )
    tag_id = SelectField(
        default=1,
        label='标签',
        validators=[
            DataRequired('请选择标签！')
        ],
        coerce=int,
        choices=[(tag.id, tag.name) for tag in Tag.query.all()],
        description='标签',
        render_kw={
            'class': "form-control"
        }
    )
    add = SubmitField(
        label='添加',
        render_kw={
            'class':'btn btn-outline-primary'
        }
    )
    delete = SubmitField(
        label="删除",
        render_kw={
            'class': 'btn-outline-success btn-sm'
        }
    )
    update = SubmitField(
        label="更新",
        render_kw={
            'class': 'btn-outline-success btn-sm'
        }
    )
