# coding:utf-8
from flask import request, url_for, render_template, flash, redirect, session, abort, current_app
from post import Post
from settings import Settings
from . import main
import app
from app.share.helper_functions import make_external
from pagination import Pagination
from user import User
from app.share.helper_functions import generate_csrf_token
from app.share.helper_functions import login_required, extract_tags
import cgi
import mistune


@main.route('/', defaults={'page': 1})
@main.route('/page-<int:page>')
def index(page):
    skip = (page - 1) * int(current_app.config['PER_PAGE'])
    posts = app.postClass.get_posts(int(current_app.config['PER_PAGE']), skip)
    count = app.postClass.get_total_count()
    pag = Pagination(page, current_app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag,
                           meta_title=current_app.config['BLOG_TITLE'])


@main.route('/logout')
def logout():
    if app.userClass.logout():
        flash('You are logged out!', 'success')
    return redirect(url_for('.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        username = request.form.get('login-username')
        password = request.form.get('login-password')
        if not username or not password:
            error = True
        else:
            user_data = app.userClass.login(username.lower().strip(), password)
            if user_data['error']:
                error = True
                error_type = 'login'
                flash(user_data['error'], 'error')
            else:
                app.userClass.start_session(user_data['data'])
                flash('You are logged in!', 'success')
                return redirect(url_for('.posts'))
    else:
        if session.get('user'):
            return redirect(url_for('.posts'))

    return render_template('login.html',
                           meta_title='Login',
                           error=error,
                           error_type=error_type)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method != 'POST':
        return redirect(url_for('.index'))

    query = request.form.get('query', None)
    if query:
        return redirect(url_for('.search_results', query=query))
    else:
        return redirect(url_for('.index'))


@main.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(400)


@main.before_request
def is_installed():
    current_app.config = app.settingsClass.get_config()
    current_app.jinja_env.globals['meta_description'] = current_app.config['BLOG_DESCRIPTION']
    if not session.get('installed', None):
        if url_for('static', filename='') not in request.path and request.path != url_for('main.install'):
            if not app.settingsClass.is_installed():
                return redirect(url_for('main.install'))


@main.before_request
def set_globals():
    # current_app.jinja_env.globals['csrf_token'] = generate_csrf_token
    # current_app.jinja_env.globals['recent_posts'] = app.postClass.get_posts(10, 0)['data']
    # current_app.jinja_env.globals['tags'] = app.postClass.get_tags()['data']
    pass


@main.route('/users')
@login_required()
def users_list():
    users = app.userClass.get_users()
    return render_template('users.html', users=users['data'], meta_title='Users')


@main.route('/posts_list', defaults={'page': 1})
@main.route('/posts_list/page-<int:page>')
@login_required()
def posts(page):
    session.pop('post-preview', None)
    skip = (page - 1) * int(current_app.config['PER_PAGE'])
    posts = app.postClass.get_posts(int(current_app.config['PER_PAGE']), skip)
    count = app.postClass.get_total_count()
    pag = Pagination(page, current_app.config['PER_PAGE'], count)

    if not posts['data']:
        abort(404)

    return render_template('posts.html', posts=posts['data'], pagination=pag, meta_title='Posts')


@main.errorhandler(404)
def page_not_found(error):
    return render_template('404.html', meta_title='404'), 404


def format_datetime_filter(input_value, format_="%Y%m%d %H:%M"):
    return input_value.strftime(format_)


@main.route('/newpost', methods=['GET', 'POST'])
@login_required()
def new_post():
    error = False
    error_type = 'validate'
    if request.method == 'POST':
        post_title = request.form.get('post-title').strip()
        post_full = request.form.get('post-full')
        post_keywords = request.form.get('post_keywords')

        if not post_title or not post_full:
            error = True
        else:
            tags = cgi.escape(request.form.get('post-tags'))
            tags_array = extract_tags(tags)

            post_short = request.form.get('post-short')
            if post_keywords.find(app.settingsClass.get_config().get('BLOG_DESCRIPTION')) < 0:
                post_keywords = app.settingsClass.get_config().get('BLOG_DESCRIPTION') + ',' + ','.join(
                    post_keywords.split(' '))
            else:
                post_keywords = ','.join(post_keywords.split(' '))
            if not post_short:
                post_short = post_full[:200]

            post_data = {'title': post_title,
                         'preview': post_short,
                         'post_keywords': post_keywords,
                         'body': post_full,
                         'tags': tags_array,
                         'author': session['user']['username']}

            post = app.postClass.validate_post_data(post_data)
            if request.form.get('post-preview') == '1':
                session['post-preview'] = post
                session[
                    'post-preview']['action'] = 'edit' if request.form.get('post-id') else 'add'
                if request.form.get('post-id'):
                    session[
                        'post-preview']['redirect'] = url_for('.post_edit', id=request.form.get('post-id'))
                else:
                    session['post-preview']['redirect'] = url_for('.new_post')
                return redirect(url_for('.post_preview'))
            else:
                session.pop('post-preview', None)

                if request.form.get('post-id'):
                    response = app.postClass.edit_post(
                        request.form['post-id'], post)
                    if not response['error']:
                        flash('Post updated!', 'success')
                    else:
                        flash(response['error'], 'error')
                    return redirect(url_for('.posts'))
                else:

                    post['view_count'] = 1

                    response = app.postClass.create_new_post(post)
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


@main.route('/install', methods=['GET', 'POST'])
def install():
    if session.get('installed', None):
        return redirect(url_for('.index'))

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
            install_result = app.settingsClass.install(blog_data, user_data)
            if install_result['error']:
                for i in install_result['error']:
                    if i is not None:
                        flash(i, 'error')
            else:
                session['installed'] = True
                flash('Successfully installed!', 'success')
                user_login = app.userClass.login(
                    user_data['_id'], user_data['new_pass'])
                if user_login['error']:
                    flash(user_login['error'], 'error')
                else:
                    app.userClass.start_session(user_login['data'])
                    flash('You are logged in!', 'success')
                    return redirect(url_for('.posts'))
    else:
        if app.settingsClass.is_installed():
            return redirect(url_for('.index'))

    return render_template('install.html',
                           default_settings=current_app.config,
                           error=error,
                           error_type=error_type,
                           meta_title='Install')


@main.route('/tag/<tag>', defaults={'page': 1})
@main.route('/tag/<tag>/page-<int:page>')
def posts_by_tag(tag, page):
    skip = (page - 1) * int(current_app.config['PER_PAGE'])
    posts = app.postClass.get_posts(int(current_app.config['PER_PAGE']), skip, tag=tag)
    count = app.postClass.get_total_count(tag=tag)
    if not posts['data']:
        abort(404)
    pag = Pagination(page, current_app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Posts by tag: ' + tag)


@main.route('/settings', methods=['GET', 'POST'])
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
            update_result = app.settingsClass.update_settings(blog_data)
            if update_result['error']:
                flash(update_result['error'], 'error')
            else:
                flash('Settings updated!', 'success')
                return redirect(url_for('.blog_settings'))

    return render_template('settings.html',
                           default_settings=current_app.config,
                           meta_title='Settings',
                           error=error,
                           error_type=error_type)


@main.route('/manage_trifles')
@login_required()
def manage_trifles():
    return render_template('manage_trifles.html')


@main.route('/post/<permalink>')
def single_post(permalink):
    from flask import Markup
    post = app.postClass.get_post_by_permalink(permalink)

    if not post['data']:
        abort(404)
    # 更新一下 访问量
    app.postClass.update_view_count(permalink)
    markdown = mistune.Markdown(escape=True, hard_wrap=True)
    b = post.get('data').get('body')
    p = post.get('data').get('preview')

    current_app.logger.warn(u"type %s" % (type(b)))
    current_app.logger.warn(u"数据库中的内容")
    current_app.logger.warn(b)
    current_app.logger.warn(u"数据库中的内容")
    current_app.logger.warn(p)
    current_app.logger.warn(post['data'].get('post_keywords'))

    current_app.logger.warn(u"markdown############")

    mk_body = markdown(b)
    preview = markdown(p)
    # app.logger.warn(mk_body)
    # app.logger.warn(u"mk_body type %s", type(mk_body))

    mk_body = Markup(mk_body)
    preview = Markup(preview)
    if not post['data'].get('post_keywords'):
        tt = post['data'].get('title').replace('  ', ' ').replace(' ', ',')
        meta_keywords = current_app.config['BLOG_DESCRIPTION'] + ',' + tt
    else:
        meta_keywords = post['data'].get('post_keywords')
        meta_keywords = meta_keywords.replace(',,', ',')
    return render_template('single_post.html', post=post['data'],
                           preview=preview, mk_body=mk_body, meta_keywords=meta_keywords,
                           meta_title=current_app.config['BLOG_TITLE'] + '::' + post['data']['title'])


@main.route('/q/<query>', defaults={'page': 1})
@main.route('/q/<query>/page-<int:page>')
def search_results(page, query):
    skip = (page - 1) * int(current_app.config['PER_PAGE'])
    if query:
        posts = app.postClass.get_posts(
            int(current_app.config['PER_PAGE']), skip, search=query)
    else:
        posts = []
        posts['data'] = []
    count = app.postClass.get_total_count(search=query)
    pag = Pagination(page, current_app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title='Search results')


@main.route('/post_preview')
@login_required()
def post_preview():
    post = session.get('post-preview')
    if not post:
        return u'<h3>session not get</h3>'
    return render_template('preview.html', post=post, meta_title='Preview post::' + post['title'])


@main.route('/post_edit?id=<id>')
@login_required()
def post_edit(id):
    post = app.postClass.get_post_by_id(id)
    if post['error']:
        flash(post['error'], 'error')
        return redirect(url_for('.posts'))

    if session.get('post-preview') and session['post-preview']['action'] == 'add':
        session.pop('post-preview', None)
    return render_template('edit_post.html',
                           meta_title='Edit post::' + post['data']['title'],
                           post=post['data'],
                           post_keywords=post['data'].get('post_keywords') or app.settingsClass.get_config().get(
                               'BLOG_DESCRIPTION'),
                           error=False,
                           error_type=False)


@main.route('/post_delete?id=<id>')
@login_required()
def post_del(id):
    if app.postClass.get_total_count() > 1:
        response = app.postClass.delete_post(id)
        if response['data'] is True:
            flash('Post removed!', 'success')
        else:
            flash(response['error'], 'error')
    else:
        flash('Need to be at least one post..', 'error')

    return redirect(url_for('.posts'))


@main.route('/recent_feed')
def recent_feed():
    return
    feed = AtomFeed(app.config['BLOG_TITLE'] + '::Recent Articles',
                    feed_url=request.url, url=request.url_root)
    posts = postClass.get_posts(int(app.config['PER_PAGE']), 0)
    for post in posts['data']:
        post_entry = post['preview'] if post['preview'] else post['body']
        feed.add(post['title'], md(post_entry),
                 content_type='html',
                 author=post['author'],
                 url=make_external(
                     url_for('.single_post', permalink=post['permalink'])),
                 updated=post['date'])
    return feed.get_response()
