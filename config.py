# coding:utf-8
"""
考虑到 有可能有多个app  这里放的是多个app 之间共享的部分
比如说 secret_key  数据库连接之类的
"""

import pymongo
import os

CONNECTION_STRING = os.environ.get('MONGO_URL')  # replace it with your settings

CONNECTION = pymongo.MongoClient(CONNECTION_STRING)

'''Leave this as is if you dont have other configuration'''
DATABASE = CONNECTION.blog
POSTS_COLLECTION = DATABASE.posts
USERS_COLLECTION = DATABASE.users
SETTINGS_COLLECTION = DATABASE.settings

# 保存上传的图片
UPDATE_INFO = DATABASE.media

ALL_SECRET_KEY = ""
basedir = os.path.abspath(os.path.dirname(__file__))
secret_file = os.path.join(basedir, '.secret')
if os.path.exists(secret_file):
    # Read SECRET_KEY from .secret file
    f = open(secret_file, 'r')
    ALL_SECRET_KEY = f.read().strip()
    f.close()
else:
    # Generate SECRET_KEY & save it away
    ALL_SECRET_KEY = os.urandom(24)
    f = open(secret_file, 'w')
    f.write(ALL_SECRET_KEY)
    f.close()
    # Modeify .gitignore to include .secret file
    gitignore_file = os.path.join(basedir, '.gitignore')
    f = open(gitignore_file, 'a+')
    if '.secret' not in f.readlines() and '.secret\n' not in f.readlines():
        f.write('.secret\n')
    f.close()

DEBUG = False  # set it to False on production

# 百度主动推送
INCLUDE_BD = True
# 再从环境中导入一下看看有没有debug文件
# --------- 重要重要重要, 永远放到最后 ----------------

try:
    from debug_config import *
except:
    pass
# --------- 仅作调试，并且不想要提交到服务器来用 ------
