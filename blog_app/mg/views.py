# coding:utf-8
from flask import render_template, redirect, url_for, current_app
from flask import request, flash, session
from . import bp
from .model import UploadForm
from blog_app.application import set_mypic
from blog_app.share.share_object import mediaClass, userClass
from blog_app.share.helper_functions import login_required
from flask import Blueprint
from blog_app.share.log import logger, flask_log


@bp.route('/')
def index():
    # rst = (list(app.mediaClass.get_all()))
    logger.error(u"ttt")
    xx = 1/0
    # flask_log.fatal(u"ttt")
    rst = current_app.config.get('UPLOADED_MYPIC_DEST')
    return render_template('mg/index.html', rst=rst)


@bp.route('/upload_img', methods=('GET', 'POST'))
@login_required()
def upload_img():
    from datetime import datetime
    import time
    form = UploadForm()
    url = None
    # app.logger.warn(u"进入函数")
    # print 'jin'
    url_list = []
    if form.validate_on_submit():
        # 因为每个图片要写上 图片说明 所有一次只能上传一张图片
        # for filename in request.files.getlist('upload'):
        # filename = form.upload.data.filename
        # print u"图片开始保存"
        # return render_template('mg/upload_img.html', form=form, url_list=url_list)
        str_folder = str(datetime.today())[:7]
        filename = form.upload.data.filename[:-4] + "_" + str(time.time())[:11]
        # print u"图片开始保存"
        # 为啥这个都会报错。。。 打印个东西。。
        url_list.append(set_mypic.url(set_mypic.save(form.upload.data, folder=str_folder, name=filename)))

        # print u"图片已经保存"
        mediaClass.set_img_info(url_list[0], filename[:-1], request.form.get('explain'))

    return render_template('mg/upload_img.html', form=form, url_list=url_list)


@bp.route('/upload_img_info')
@login_required()
def get_img_info():
    rst_img_list = mediaClass.get_all()
    # app.logger.error(rst_img_list)
    return render_template('mg/img_info.html', rst_img_list=rst_img_list)


@bp.route('/add_user')
@login_required()
def add_user():
    gravatar_url = userClass.get_gravatar_link()
    return render_template('mg/add_user.html', gravatar_url=gravatar_url, meta_title='Add user')


@bp.route('/edit_user?id=<id>')
@login_required()
def edit_user(id):
    user = userClass.get_user(id)
    return render_template('mg/edit_user.html', user=user['data'], meta_title='Edit user')


@bp.route('/delete_user?id=<id>')
@login_required()
def delete_user(id):
    if id != session['user']['username']:
        user = userClass.delete_user(id)
        if user['error']:
            flash(user['error'], 'error')
        else:
            flash('User deleted!', 'success')
    return redirect(url_for('.users_list'))


@bp.route('/save_user', methods=['POST'])
@login_required()
def save_user():
    post_data = {
        '_id': request.form.get('user-id', None).lower().strip(),
        'email': request.form.get('user-email', None),
        'old_pass': request.form.get('user-old-password', None),
        'new_pass': request.form.get('user-new-password', None),
        'new_pass_again': request.form.get('user-new-password-again', None),
        'update': request.form.get('user-update', False)
    }
    if not post_data['email'] or not post_data['_id']:
        flash('Username and Email are required..', 'error')
        if post_data['update']:
            return redirect(url_for('.edit_user', id=post_data['_id']))
        else:
            return redirect(url_for('.add_user'))
    else:
        user = userClass.save_user(post_data)
        if user['error']:
            flash(user['error'], 'error')
            if post_data['update']:
                return redirect(url_for('.edit_user', id=post_data['_id']))
            else:
                return redirect(url_for('.add_user'))
        else:
            message = 'User updated!' if post_data['update'] else 'User added!'
            flash(message, 'success')
    return redirect(url_for('.edit_user', id=post_data['_id']))
