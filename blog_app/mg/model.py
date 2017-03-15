# coding:utf-8
from flask_wtf import Form
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from blog_app.application import set_mypic


class UploadForm(Form):
    """
    一个简单的上传表单
    """
    # 文件field设置为‘必须的’，过滤规则设置为‘set_mypic’
    upload = FileField('image', validators=[
        FileRequired(), FileAllowed(set_mypic, 'you can upload images only!')])
    explain = StringField(u'图片说明', validators=[DataRequired()])
    submit = SubmitField('ok')
