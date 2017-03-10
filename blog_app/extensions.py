# coding:utf-8
from flask.ext.moment import Moment,_moment
from flask_bootstrap import Bootstrap
from flask_script import Manager

from flask_uploads import UploadSet

bootstrap = Bootstrap()
manager = Manager()


# md = Markdown()
# 新建一个set用于设置文件类型、过滤等
set_mypic = UploadSet('mypic')  # mypic