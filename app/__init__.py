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
from main.user import User
from main.settings import Settings
from main.post import Post
from share.media import Media

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

    # mypic 的存储位置,
    # UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
    app.config['UPLOADED_MYPIC_DEST'] = './media/img/'

    # mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
    app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES

    from .main import main as main_bp
    app.register_blueprint(main_bp, url_prefix='/')

    from .mg import mg as mg_bl
    app.register_blueprint(mg_bl, url_prefix='/mg')

    return app