# coding:utf-8
from flask import Flask
from flask.ext.moment import Moment
from flask_bootstrap import Bootstrap
from flask_script import Manager
from flask_uploads import UploadSet, IMAGES
from flaskext.markdown import Markdown
from app.share.helper_functions import *
from mdx_code_multiline import MultilineCodeExtension
from mdx_github_gists import GitHubGistExtension
from mdx_quote import QuoteExtension
from mdx_strike import StrikeExtension
from app.main.user import User
from app.main.settings import Settings
from app.main.post import Post
from app.share.media import Media
import app as app_model
from app.main.views import format_datetime_filter

bootstrap = Bootstrap()
manager = Manager()

postClass = Post()
userClass = User()
settingsClass = Settings()
mediaClass = Media()

# md = Markdown()
# 新建一个set用于设置文件类型、过滤等
set_mypic = UploadSet('mypic')  # mypic


def create_app():
    app = Flask(__name__)
    moment = Moment(app)

    md = Markdown(app)
    md.register_extension(GitHubGistExtension)
    md.register_extension(StrikeExtension)
    md.register_extension(QuoteExtension)
    md.register_extension(MultilineCodeExtension)
    app.config.from_object('config')
    bootstrap.init_app(app)

    userClass.init(app.config)
    postClass.init(app.config)
    settingsClass.init(app.config)
    mediaClass.init(app.config)

    # 初始化一些 jinjia2 模板里面的自定义函数
    app.add_template_global(generate_csrf_token, 'csrf_token')
    app.add_template_global(app_model.postClass.get_posts(10, 0)['data'], 'recent_posts')
    app.add_template_global(app_model.postClass.get_tags()['data'], 'tags')
    app.add_template_global(url_for_other_page, 'url_for_other_page')
    app.add_template_global(app.config['BLOG_DESCRIPTION'], 'meta_description')
    app.add_template_filter(format_datetime_filter, 'formatdate')

    # mypic 的存储位置,
    # UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
    app.config['UPLOADED_MYPIC_DEST'] = './media/img/'

    # mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
    app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES

    from .main import main as main_bp
    # 额 这后面的 url_prefix='/' 不要加 默认就是这个 加了 反而解析不了
    app.register_blueprint(main_bp)

    from .mg import mg as mg_bl
    app.register_blueprint(mg_bl, url_prefix='/mg')

    if not app.config['DEBUG']:
        import logging
        from logging import FileHandler
        file_handler = FileHandler(app.config['LOG_FILE'])
        file_handler.setLevel(logging.WARNING)
        app.logger.addHandler(file_handler)

    return app
