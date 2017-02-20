#coding:utf-8
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
from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_bootstrap import Bootstrap
# from forms import UploadForm

app = Flask('FlaskBlog')
moment = Moment(app)

md = Markdown(app)
md.register_extension(GitHubGistExtension)
md.register_extension(StrikeExtension)
md.register_extension(QuoteExtension)
md.register_extension(MultilineCodeExtension)
app.config.from_object('config')

# 新建一个set用于设置文件类型、过滤等
set_mypic = UploadSet('mypic')  # mypic

# 用于wtf.quick_form()模版渲染
bootstrap = Bootstrap(app)

# mypic 的存储位置,
# UPLOADED_xxxxx_DEST, xxxxx部分就是定义的set的名称, mypi, 下同
app.config['UPLOADED_MYPIC_DEST'] = './media/img/'

# mypic 允许存储的类型, IMAGES为预设的 tuple('jpg jpe jpeg png gif svg bmp'.split())
app.config['UPLOADED_MYPIC_ALLOW'] = IMAGES

# 把刚刚app设置的config注册到set_mypic
configure_uploads(app, set_mypic)
#####
class UploadForm(Form):
    """
    一个简单的上传表单
    """
    # 文件field设置为‘必须的’，过滤规则设置为‘set_mypic’
    upload = FileField('image', validators=[
        FileRequired(), FileAllowed(set_mypic, 'you can upload images only!')])
    submit = SubmitField('ok')
#####

@app.route('/', defaults={'page': 1})
@app.route('/page-<int:page>')
def index(page):
    skip = (page - 1) * int(app.config['PER_PAGE'])
    posts = postClass.get_posts(int(app.config['PER_PAGE']), skip)
    count = postClass.get_total_count()
    pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title=app.config['BLOG_TITLE'])


@app.route('/tag/<tag>', defaults={'page': 1})
@app.route('/tag/<tag>/page-<int:page>')
def posts_by_tag(tag, page):
    skip = (page - 1) * int(app.config['PER_PAGE'])
    posts = postClass.get_posts(int(app.config['PER_PAGE']), skip, tag=tag)
    count = postClass.get_total_count(tag=tag)
    if not posts['data']:
        abort(404)
    pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Posts by tag: ' + tag)


@app.route('/post/<permalink>')
def single_post(permalink):
    from flask import Markup
    post = postClass.get_post_by_permalink(permalink)

    if not post['data']:
        abort(404)
    # 更新一下 访问量
    postClass.update_view_count(permalink)
    markdown = mistune.Markdown(escape=True, hard_wrap=True)
    b = post.get('data').get('body')
    p = post.get('data').get('preview')

    app.logger.warn(u"type %s" %(type(b)))
    app.logger.warn(u"数据库中的内容")
    app.logger.warn(b)

    app.logger.warn(u"markdown############")

    mk_body = markdown(b)
    preview = markdown(p)
    # app.logger.warn(mk_body)
    # app.logger.warn(u"mk_body type %s", type(mk_body))

    mk_body = Markup(mk_body)
    return render_template('single_post.html', post=post['data'], preview=preview, mk_body=mk_body,meta_title=app.config['BLOG_TITLE'] + '::' + post['data']['title'])


@app.route('/q/<query>', defaults={'page': 1})
@app.route('/q/<query>/page-<int:page>')
def search_results(page, query):
    skip = (page - 1) * int(app.config['PER_PAGE'])
    if query:
        posts = postClass.get_posts(
            int(app.config['PER_PAGE']), skip, search=query)
    else:
        posts = []
        posts['data'] = []
    count = postClass.get_total_count(search=query)
    pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Search results')


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method != 'POST':
        return redirect(url_for('index'))

    query = request.form.get('query', None)
    if query:
        return redirect(url_for('search_results', query=query))
    else:
        return redirect(url_for('index'))


@app.route('/newpost', methods=['GET', 'POST'])
@login_required()
def new_post():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        post_title = request.form.get('post-title').strip()
        post_full = request.form.get('post-full')

        if not post_title or not post_full:
            error = True
        else:
            tags = cgi.escape(request.form.get('post-tags'))
            tags_array = extract_tags(tags)

            post_short = request.form.get('post-short')
            if not post_short:
                post_short = post_full[:200]

            post_data = {'title': post_title,
                         'preview': post_short,
                         'body': post_full,
                         'tags': tags_array,
                         'author': session['user']['username']}

            post = postClass.validate_post_data(post_data)
            if request.form.get('post-preview') == '1':
                session['post-preview'] = post
                session[
                    'post-preview']['action'] = 'edit' if request.form.get('post-id') else 'add'
                if request.form.get('post-id'):
                    session[
                        'post-preview']['redirect'] = url_for('post_edit', id=request.form.get('post-id'))
                else:
                    session['post-preview']['redirect'] = url_for('new_post')
                return redirect(url_for('post_preview'))
            else:
                session.pop('post-preview', None)

                if request.form.get('post-id'):
                    response = postClass.edit_post(
                        request.form['post-id'], post)
                    if not response['error']:
                        flash('Post updated!', 'success')
                    else:
                        flash(response['error'], 'error')
                    return redirect(url_for('posts'))
                else:

                    post['view_count'] = 1

                    response = postClass.create_new_post(post)
                    if response['error']:
                        error = True
                        error_type = 'post'
                        flash(response['error'], 'error')
                    else:
                        flash('New post created!', 'success')
    else:
        if session.get('post-preview') and session['post-preview']['action'] == 'edit':
            session.pop('post-preview', None)
    return render_template('new_post.html',
                           meta_title='New post',
                           error=error,
                           error_type=error_type)


@app.route('/post_preview')
@login_required()
def post_preview():
    post = session.get('post-preview')
    return render_template('preview.html', post=post, meta_title='Preview post::' + post['title'])


@app.route('/posts_list', defaults={'page': 1})
@app.route('/posts_list/page-<int:page>')
@login_required()
def posts(page):
    session.pop('post-preview', None)
    skip = (page - 1) * int(app.config['PER_PAGE'])
    posts = postClass.get_posts(int(app.config['PER_PAGE']), skip)
    count = postClass.get_total_count()
    pag = pagination.Pagination(page, app.config['PER_PAGE'], count)

    if not posts['data']:
        abort(404)

    return render_template('posts.html', posts=posts['data'], pagination=pag, meta_title='Posts')


@app.route('/post_edit?id=<id>')
@login_required()
def post_edit(id):
    post = postClass.get_post_by_id(id)
    if post['error']:
        flash(post['error'], 'error')
        return redirect(url_for('posts'))

    if session.get('post-preview') and session['post-preview']['action'] == 'add':
        session.pop('post-preview', None)
    return render_template('edit_post.html',
                           meta_title='Edit post::' + post['data']['title'],
                           post=post['data'],
                           error=False,
                           error_type=False)


@app.route('/post_delete?id=<id>')
@login_required()
def post_del(id):
    if postClass.get_total_count() > 1:
        response = postClass.delete_post(id)
        if response['data'] is True:
            flash('Post removed!', 'success')
        else:
            flash(response['error'], 'error')
    else:
        flash('Need to be at least one post..', 'error')

    return redirect(url_for('posts'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        username = request.form.get('login-username')
        password = request.form.get('login-password')
        if not username or not password:
            error = True
        else:
            user_data = userClass.login(username.lower().strip(), password)
            if user_data['error']:
                error = True
                error_type = 'login'
                flash(user_data['error'], 'error')
            else:
                userClass.start_session(user_data['data'])
                flash('You are logged in!', 'success')
                return redirect(url_for('posts'))
    else:
        if session.get('user'):
            return redirect(url_for('posts'))

    return render_template('login.html',
                           meta_title='Login',
                           error=error,
                           error_type=error_type)


@app.route('/logout')
def logout():
    if userClass.logout():
        flash('You are logged out!', 'success')
    return redirect(url_for('login'))


@app.route('/users')
@login_required()
def users_list():
    users = userClass.get_users()
    return render_template('users.html', users=users['data'], meta_title='Users')


@app.route('/add_user')
@login_required()
def add_user():
    gravatar_url = userClass.get_gravatar_link()
    return render_template('add_user.html', gravatar_url=gravatar_url, meta_title='Add user')


@app.route('/edit_user?id=<id>')
@login_required()
def edit_user(id):
    user = userClass.get_user(id)
    return render_template('edit_user.html', user=user['data'], meta_title='Edit user')


@app.route('/delete_user?id=<id>')
@login_required()
def delete_user(id):
    if id != session['user']['username']:
        user = userClass.delete_user(id)
        if user['error']:
            flash(user['error'], 'error')
        else:
            flash('User deleted!', 'success')
    return redirect(url_for('users_list'))


@app.route('/save_user', methods=['POST'])
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
                return redirect(url_for('edit_user', id=post_data['_id']))
        else:
            return redirect(url_for('add_user'))
    else:
        user = userClass.save_user(post_data)
        if user['error']:
            flash(user['error'], 'error')
            if post_data['update']:
                return redirect(url_for('edit_user', id=post_data['_id']))
            else:
                return redirect(url_for('add_user'))
        else:
            message = 'User updated!' if post_data['update'] else 'User added!'
            flash(message, 'success')
    return redirect(url_for('edit_user', id=post_data['_id']))


@app.route('/recent_feed')
def recent_feed():
    feed = AtomFeed(app.config['BLOG_TITLE'] + '::Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = postClass.get_posts(int(app.config['PER_PAGE']), 0)
    for post in posts['data']:
        post_entry = post['preview'] if post['preview'] else post['body']
        feed.add(post['title'], md(post_entry),
                 content_type='html',
                 author=post['author'],
                 url=make_external(
                     url_for('single_post', permalink=post['permalink'])),
                 updated=post['date'])
    return feed.get_response()


@app.route('/settings', methods=['GET', 'POST'])
@login_required()
def blog_settings():
    error = None
    error_type = 'validate'
    if request.method == 'POST':
        blog_data = {
            'title': request.form.get('blog-title', None),
            'description': request.form.get('blog-description', None),
            'per_page': request.form.get('blog-perpage', None),
            'text_search': request.form.get('blog-text-search', None)
        }
        blog_data['text_search'] = 1 if blog_data['text_search'] else 0
        for key, value in blog_data.items():
            if not value and key != 'text_search' and key != 'description':
                error = True
                break
        if not error:
            update_result = settingsClass.update_settings(blog_data)
            if update_result['error']:
                flash(update_result['error'], 'error')
            else:
                flash('Settings updated!', 'success')
                return redirect(url_for('blog_settings'))

    return render_template('settings.html',
                           default_settings=app.config,
                           meta_title='Settings',
                           error=error,
                           error_type=error_type)

################
@app.route('/upload_img', methods=('GET', 'POST'))
def upload_img():

    form = UploadForm()
    url = None
    app.logger.warn(u"进入函数")
    url_list = []
    if form.validate_on_submit():
        # filename = form.upload.data.filename
        for filename in request.files.getlist('upload'):
            url_list.append(set_mypic.url(set_mypic.save(filename)))
    return render_template('upload_img.html', form=form, url_list=url_list)

################


@app.route('/imgupload', methods=['GET', 'POST'])
def img_upload():
    img_data = request.form.get('imgupload', None)
    if not img_data:
        current_app.logging.error("is ok")
        return render_template('upload_img.html')
    else:
        current_app.logging.error("is ok")
        return '<h1>ok!!</hl>'

@app.route('/install', methods=['GET', 'POST'])
def install():
    if session.get('installed', None):
        return redirect(url_for('index'))

    error = False
    error_type = 'validate'
    if request.method == 'POST':
        user_error = False
        blog_error = False

        user_data = {
            '_id': request.form.get('user-id', None).lower().strip(),
            'email': request.form.get('user-email', None),
            'new_pass': request.form.get('user-new-password', None),
            'new_pass_again': request.form.get('user-new-password-again', None),
            'update': False
        }
        blog_data = {
            'title': request.form.get('blog-title', None),
            'description': request.form.get('blog-description', None),
            'per_page': request.form.get('blog-perpage', None),
            'text_search': request.form.get('blog-text-search', None)
        }
        blog_data['text_search'] = 1 if blog_data['text_search'] else 0

        for key, value in user_data.items():
            if not value and key != 'update':
                user_error = True
                break
        for key, value in blog_data.items():
            if not value and key != 'text_search' and key != 'description':
                blog_error = True
                break

        if user_error or blog_error:
            error = True
        else:
            install_result = settingsClass.install(blog_data, user_data)
            if install_result['error']:
                for i in install_result['error']:
                    if i is not None:
                        flash(i, 'error')
            else:
                session['installed'] = True
                flash('Successfully installed!', 'success')
                user_login = userClass.login(
                    user_data['_id'], user_data['new_pass'])
                if user_login['error']:
                    flash(user_login['error'], 'error')
                else:
                    userClass.start_session(user_login['data'])
                    flash('You are logged in!', 'success')
                    return redirect(url_for('posts'))
    else:
        if settingsClass.is_installed():
            return redirect(url_for('index'))

    return render_template('install.html',
                           default_settings=app.config,
                           error=error,
                           error_type=error_type,
                           meta_title='Install')


@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(400)


@app.before_request
def is_installed():
    app.config = settingsClass.get_config()
    app.jinja_env.globals['meta_description'] = app.config['BLOG_DESCRIPTION']
    if not session.get('installed', None):
        if url_for('static', filename='') not in request.path and request.path != url_for('install'):
            if not settingsClass.is_installed():
                return redirect(url_for('install'))


@app.before_request
def set_globals():
    app.jinja_env.globals['csrf_token'] = generate_csrf_token
    app.jinja_env.globals['recent_posts'] = postClass.get_posts(10, 0)['data']
    app.jinja_env.globals['tags'] = postClass.get_tags()['data']


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', meta_title='404'), 404


@app.template_filter('formatdate')
def format_datetime_filter(input_value, format_="%a, %d %b %Y"):
    return input_value.strftime(format_)


settingsClass = settings.Settings(app.config)
postClass = post.Post(app.config)
userClass = user.User(app.config)

app.jinja_env.globals['url_for_other_page'] = url_for_other_page
app.jinja_env.globals['meta_description'] = app.config['BLOG_DESCRIPTION']

if not app.config['DEBUG']:
    import logging
    from logging import FileHandler
    file_handler = FileHandler(app.config['LOG_FILE'])
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)),
            debug=app.config['DEBUG'])
