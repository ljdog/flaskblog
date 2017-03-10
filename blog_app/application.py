# coding:utf-8
from flask import Flask

from flask_uploads import UploadSet, IMAGES, configure_uploads
from flaskext.markdown import Markdown
from blog_app.share.helper_functions import generate_csrf_token, url_for_other_page
from mdx_code_multiline import MultilineCodeExtension
from mdx_github_gists import GitHubGistExtension
from mdx_quote import QuoteExtension
from mdx_strike import StrikeExtension
from extensions import bootstrap, manager, set_mypic
from blog_app.share.helper_functions import format_datetime_filter
import os
from importlib import import_module
from blog_app.share import postClass, userClass, settingsClass, mediaClass

from share.log import logger




def create_app(config=None, name=None):
    if config is None:
        config = 'app_config.py'

    if not name:
        name = __name__

    app = Flask(name)

    app.config.from_pyfile(config)

    configure_logging(app)
    configure_extensions(app)
    configure_context_processors(app)
    configure_handlers(app)
    configure_views(app)

    logger.debug(u"url_map %s", app.url_map)
    logger.debug(u"view_functions %s", app.view_functions)
    return app


def configure_logging(app):
    import logging.config
    app.logger and logging.config.dictConfig(app.config['LOGGING'])


def configure_extensions(app):
    """
    初始化插件
    """
    md = Markdown(app)
    md.register_extension(GitHubGistExtension)
    md.register_extension(StrikeExtension)
    md.register_extension(QuoteExtension)
    md.register_extension(MultilineCodeExtension)

    bootstrap.init_app(app)

    userClass.init(app.config)
    postClass.init(app.config)
    settingsClass.init(app.config)
    mediaClass.init(app.config)

    # mypic 的存储位置,
    # UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
    app.config['UPLOADED_MYPIC_DEST'] = os.getcwd() + '/media/img'

    # mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
    app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES
    configure_uploads(app, set_mypic)

    # @login_manager.user_loader
    # def load_user(userid):
    #     return models.User.query.get(userid)
    #
    # babel.init_app(app)


def configure_context_processors(app):
    """
    模板变量
    """
    # 初始化一些 jinjia2 模板里面的自定义函数
    app.add_template_global(generate_csrf_token, 'csrf_token')
    app.add_template_global(postClass.get_posts(10, 0)['data'], 'recent_posts')
    app.add_template_global(postClass.get_tags()['data'], 'tags')
    app.add_template_global(url_for_other_page, 'url_for_other_page')
    app.add_template_global(app.config['BLOG_DESCRIPTION'], 'meta_description')
    app.add_template_filter(format_datetime_filter, 'formatdate')


def configure_handlers(app):
    """
    before_request之类的处理
    """
    pass


def configure_views(app):
    """
    注册views
    """
    # BLUEPRINTS = (
    #     ('blog_app.main', ''),
    #     ('blog_app.mg', '/mg'),
    # )
    from blog_app.main import bp as main_bp
    from blog_app.mg.views import bp
    app.register_blueprint(main_bp)
    app.register_blueprint(bp, url_prefix='/mg')
    # for it in app.config['BLUEPRINTS']:
    #     logger.debug(u"it %s", it)
    #     app.register_blueprint(import_module(it[0]).bp, url_prefix=it[1])
    logger.debug(u"blueprints %s", app.blueprints)
