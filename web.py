#
#
#
#
#
# #####
#

#
#
# @app.route('/tag/<tag>', defaults={'page': 1})
# @app.route('/tag/<tag>/page-<int:page>')
# def posts_by_tag(tag, page):
#     skip = (page - 1) * int(app.config['PER_PAGE'])
#     posts = postClass.get_posts(int(app.config['PER_PAGE']), skip, tag=tag)
#     count = postClass.get_total_count(tag=tag)
#     if not posts['data']:
#         abort(404)
#     pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
#     return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Posts by tag: ' + tag)
#
#
#

#
#
# @app.route('/post/<permalink>')
# def single_post(permalink):
#     from flask import Markup
#     post = postClass.get_post_by_permalink(permalink)
#
#     if not post['data']:
#         abort(404)
#     # 更新一下 访问量
#     postClass.update_view_count(permalink)
#     markdown = mistune.Markdown(escape=True, hard_wrap=True)
#     b = post.get('data').get('body')
#     p = post.get('data').get('preview')
#
#     app.logger.warn(u"type %s" %(type(b)))
#     app.logger.warn(u"数据库中的内容")
#     app.logger.warn(b)
#     app.logger.warn(u"数据库中的内容")
#     app.logger.warn(p)
#
#     app.logger.warn(u"markdown############")
#
#     mk_body = markdown(b)
#     preview = markdown(p)
#     # app.logger.warn(mk_body)
#     # app.logger.warn(u"mk_body type %s", type(mk_body))
#
#     mk_body = Markup(mk_body)
#     preview = Markup(preview)
#     return render_template('single_post.html', post=post['data'], preview=preview, mk_body=mk_body, meta_title=app.config['BLOG_TITLE'] + '::' + post['data']['title'])
#
#
# @app.route('/q/<query>', defaults={'page': 1})
# @app.route('/q/<query>/page-<int:page>')
# def search_results(page, query):
#     skip = (page - 1) * int(app.config['PER_PAGE'])
#     if query:
#         posts = postClass.get_posts(
#             int(app.config['PER_PAGE']), skip, search=query)
#     else:
#         posts = []
#         posts['data'] = []
#     count = postClass.get_total_count(search=query)
#     pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
#     return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Search results')
#
#

#

#
# @app.route('/post_preview')
# @login_required()
# def post_preview():
#     post = session.get('post-preview')
#     if not post:
#         return u'<h3>session not get</h3>'
#     return render_template('preview.html', post=post, meta_title='Preview post::' + post['title'])
#
#

#
# @app.route('/post_edit?id=<id>')
# @login_required()
# def post_edit(id):
#     post = postClass.get_post_by_id(id)
#     if post['error']:
#         flash(post['error'], 'error')
#         return redirect(url_for('posts'))
#
#     if session.get('post-preview') and session['post-preview']['action'] == 'add':
#         session.pop('post-preview', None)
#     return render_template('edit_post.html',
#                            meta_title='Edit post::' + post['data']['title'],
#                            post=post['data'],
#                            error=False,
#                            error_type=False)
#
#
# @app.route('/post_delete?id=<id>')
# @login_required()
# def post_del(id):
#     if postClass.get_total_count() > 1:
#         response = postClass.delete_post(id)
#         if response['data'] is True:
#             flash('Post removed!', 'success')
#         else:
#             flash(response['error'], 'error')
#     else:
#         flash('Need to be at least one post..', 'error')
#
#     return redirect(url_for('posts'))
#
#

#

#
#

#
# @app.route('/add_user')
# @login_required()
# def add_user():
#     gravatar_url = userClass.get_gravatar_link()
#     return render_template('add_user.html', gravatar_url=gravatar_url, meta_title='Add user')
#
#
# @app.route('/edit_user?id=<id>')
# @login_required()
# def edit_user(id):
#     user = userClass.get_user(id)
#     return render_template('edit_user.html', user=user['data'], meta_title='Edit user')
#
#
# @app.route('/delete_user?id=<id>')
# @login_required()
# def delete_user(id):
#     if id != session['user']['username']:
#         user = userClass.delete_user(id)
#         if user['error']:
#             flash(user['error'], 'error')
#         else:
#             flash('User deleted!', 'success')
#     return redirect(url_for('users_list'))
#
#
# @app.route('/save_user', methods=['POST'])
# @login_required()
# def save_user():
#     post_data = {
#         '_id': request.form.get('user-id', None).lower().strip(),
#         'email': request.form.get('user-email', None),
#         'old_pass': request.form.get('user-old-password', None),
#         'new_pass': request.form.get('user-new-password', None),
#         'new_pass_again': request.form.get('user-new-password-again', None),
#         'update': request.form.get('user-update', False)
#     }
#     if not post_data['email'] or not post_data['_id']:
#         flash('Username and Email are required..', 'error')
#         if post_data['update']:
#                 return redirect(url_for('edit_user', id=post_data['_id']))
#         else:
#             return redirect(url_for('add_user'))
#     else:
#         user = userClass.save_user(post_data)
#         if user['error']:
#             flash(user['error'], 'error')
#             if post_data['update']:
#                 return redirect(url_for('edit_user', id=post_data['_id']))
#             else:
#                 return redirect(url_for('add_user'))
#         else:
#             message = 'User updated!' if post_data['update'] else 'User added!'
#             flash(message, 'success')
#     return redirect(url_for('edit_user', id=post_data['_id']))
#
#

#
#

#
# ################
#
# ################
#
#
# @app.route('/imgupload', methods=['GET', 'POST'])
# def img_upload():
#     img_data = request.form.get('imgupload', None)
#     if not img_data:
#         current_app.logging.error("is ok")
#         return render_template('upload_img.html')
#     else:
#         current_app.logging.error("is ok")
#         return '<h1>ok!!</hl>'
#
# @app.route('/install', methods=['GET', 'POST'])
# def install():
#     if session.get('installed', None):
#         return redirect(url_for('index'))
#
#     error = False
#     error_type = 'validate'
#     if request.method == 'POST':
#         user_error = False
#         blog_error = False
#
#         user_data = {
#             '_id': request.form.get('user-id', None).lower().strip(),
#             'email': request.form.get('user-email', None),
#             'new_pass': request.form.get('user-new-password', None),
#             'new_pass_again': request.form.get('user-new-password-again', None),
#             'update': False
#         }
#         blog_data = {
#             'title': request.form.get('blog-title', None),
#             'description': request.form.get('blog-description', None),
#             'per_page': request.form.get('blog-perpage', None),
#             'text_search': request.form.get('blog-text-search', None)
#         }
#         blog_data['text_search'] = 1 if blog_data['text_search'] else 0
#
#         for key, value in user_data.items():
#             if not value and key != 'update':
#                 user_error = True
#                 break
#         for key, value in blog_data.items():
#             if not value and key != 'text_search' and key != 'description':
#                 blog_error = True
#                 break
#
#         if user_error or blog_error:
#             error = True
#         else:
#             install_result = settingsClass.install(blog_data, user_data)
#             if install_result['error']:
#                 for i in install_result['error']:
#                     if i is not None:
#                         flash(i, 'error')
#             else:
#                 session['installed'] = True
#                 flash('Successfully installed!', 'success')
#                 user_login = userClass.login(
#                     user_data['_id'], user_data['new_pass'])
#                 if user_login['error']:
#                     flash(user_login['error'], 'error')
#                 else:
#                     userClass.start_session(user_login['data'])
#                     flash('You are logged in!', 'success')
#                     return redirect(url_for('posts'))
#     else:
#         if settingsClass.is_installed():
#             return redirect(url_for('index'))
#
#     return render_template('install.html',
#                            default_settings=app.config,
#                            error=error,
#                            error_type=error_type,
#                            meta_title='Install')
#
#

#
# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html', meta_title='404'), 404
#
#
# @app.template_filter('formatdate')
# def format_datetime_filter(input_value, format_="%a, %d %b %Y"):
#     return input_value.strftime(format_)
#
#
# settingsClass = settings.Settings(app.config)
#
#
# app.jinja_env.globals['url_for_other_page'] = url_for_other_page
# app.jinja_env.globals['meta_description'] = app.config['BLOG_DESCRIPTION']
#
# if not app.config['DEBUG']:
#     import logging
#     from logging import FileHandler
#     file_handler = FileHandler(app.config['LOG_FILE'])
#     file_handler.setLevel(logging.WARNING)
#     app.logger.addHandler(file_handler)
#
# if __name__ == '__main__':
#     app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)),
#             debug=app.config['DEBUG'])
