# coding:utf-8
from . import mg as mg_bp
from .model import UploadForm
from .. import set_mypic
from ..share.helper_functions import login_required
import config
from flask import render_template
from ..share.media import Media
from manage import app

mediaClass = Media(app.config)

@mg_bp.route('/')
def index():
    return 'mg index'

@mg_bp.route('/upload_img', methods=('GET', 'POST'))
# @login_required()
def upload_img(request):
    from datetime import datetime
    import time
    form = UploadForm()
    url = None
    app.logger.warn(u"进入函数")
    url_list = []
    if form.validate_on_submit():
        # 因为每个图片要写上 图片说明 所有一次只能上传一张图片
        # for filename in request.files.getlist('upload'):
        # filename = form.upload.data.filename
        str_folder = str(datetime.today())[:7]
        filename = form.upload.data.filename[:-4] + "_" + str(time.time())[:11]
        url_list.append(set_mypic.url(set_mypic.save(form.upload.data, folder=str_folder, name=filename)))

        mediaClass.set_img_info(url_list[0], filename[:-1], request.form.get('explain'))

    return render_template('upload_img.html', form=form, url_list=url_list)


@mg_bp.route('/upload_img_info')
#@login_required()
def get_img_info():
    rst_img_list = mediaClass.get_all()
    return render_template('img_info.html', rst_img_list=rst_img_list)

