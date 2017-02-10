# coding:utf-8

from flask.ext.uploads import UploadSet
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import Form
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from web import set_mypic

class UploadForm(Form):
    """
    一个简单的上传表单
    """
    # 文件field设置为‘必须的’，过滤规则设置为‘set_mypic’
    upload = FileField('image', validators=[
        FileRequired(), FileAllowed(set_mypic, 'you can upload images only!')])
    submit = SubmitField('ok')
