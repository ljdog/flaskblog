# -*- coding: utf-8 -*-
"""
仅存放如下类型配置: flask自身配置，flask.ext配置，blueprint之间共享的配置
至于仅在单独模块下使用的，放到各自模块下即可
"""

import os
from config import ALL_SECRET_KEY
from config import DATABASE, POSTS_COLLECTION, USERS_COLLECTION, SETTINGS_COLLECTION

POSTS_COLLECTION = POSTS_COLLECTION
USERS_COLLECTION = USERS_COLLECTION
SETTINGS_COLLECTION = SETTINGS_COLLECTION

# 保存上传的图片
UPDATE_INFO = DATABASE.media


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEV_MODE = 'DEV'
MODE = os.environ.get('MODE')

DEBUG = MODE == DEV_MODE

SECRET_KEY = ALL_SECRET_KEY

BLUEPRINTS = (
    ('blog_app.main.views', ''),
    ('blog_app.mg', '/mg'),
)

LOGGER_NAME = 'flask'

FLASK_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/flask.log")
MAIN_LOG_FILE_PATH = os.path.join(BASE_DIR, "logs/main.log")

LOG_FORMAT = '\n'.join((
    '/' + '-' * 80,
    '[%(levelname)s][%(asctime)s][%(process)d:%(thread)d][%(filename)s:%(lineno)d %(funcName)s]:',
    '%(message)s',
    '-' * 80 + '/',
))

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,

    'formatters': {
        'standard': {
            'format': LOG_FORMAT,
        },
    },

    'handlers': {
        'flask_flylog': {
            'level': 'ERROR',
            'class': 'flylog.LogHandler',
            'formatter': 'standard',
            'source': os.path.basename(BASE_DIR),
        },
        'flylog': {
            'level': 'CRITICAL',
            'class': 'flylog.LogHandler',
            'formatter': 'standard',
            'source': os.path.basename(BASE_DIR),
        },
        'flask_rfile': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': FLASK_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'main_rfile': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'filename': MAIN_LOG_FILE_PATH,
            'maxBytes': 1024 * 1024 * 500,  # 500 MB
            'backupCount': 5,
        },
        'console': {
            'level': 'DEBUG' if DEBUG else 'CRITICAL',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },

    'loggers': {
        'flask': {
            'handlers': ['console', 'flask_rfile', 'flask_flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
        'main': {
            'handlers': ['console', 'main_rfile', 'flylog'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

# flask-sqlalchemy
# SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(BASE_DIR, 'db.sqlite')
# SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/flask_dpl'
# SQLALCHEMY_ECHO = False

# flask-babel
BABEL_DEFAULT_LOCALE = 'zh_CN'
BABEL_DEFAULT_TIMEZONE = 'Asia/Shanghai'

# admin_user
# SESSION_KEY_ADMIN_USERNAME = 'admin_username'
