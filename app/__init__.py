# coding:utf-8
import cgi
import os
from flask import Flask, render_template, abort, url_for, request, flash, session, redirect
from flaskext.markdown import Markdown
from mdx_github_gists import GitHubGistExtension
from mdx_strike import StrikeExtension
from mdx_quote import QuoteExtension
from mdx_code_multiline import MultilineCodeExtension
from werkzeug.contrib.atom import AtomFeed
import post
import user
import media
import mistune
import pagination
import settings
from helper_functions import *
from flask.ext.moment import Moment
from flask import current_app


from flask.ext.uploads import UploadSet
from flask_bootstrap import Bootstrap
from flask import Flask, render_template
from flask_uploads import UploadSet, IMAGES, configure_uploads
from flask_wtf import Form
from wtforms import SubmitField,StringField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
bootstrap = Bootstrap()



def create_app():
    app = Flask('FlaskBlog')
    moment = Moment(app)

    md = Markdown(app)
    md.register_extension(GitHubGistExtension)
    md.register_extension(StrikeExtension)
    md.register_extension(QuoteExtension)
    md.register_extension(MultilineCodeExtension)
    app.config.from_object('config')
    bootstrap.init_app(app)
    
    # 新建一个set用于设置文件类型、过滤等
    set_mypic = UploadSet('mypic')  # mypic
    # mypic 的存储位置,
    # UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
    app.config['UPLOADED_MYPIC_DEST'] = './media/img/'

    # mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
    app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES
    return app