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


@main.route('/', defaults={'page': 1})
@main.route('/page-<int:page>')
def index(page):
    skip = (page - 1) * int(current_app.config['PER_PAGE'])
    posts = app.postClass.get_posts(int(current_app.config['PER_PAGE']), skip)
    count = app.postClass.get_total_count()
    pag = Pagination(page, current_app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title=app.config['BLOG_TITLE'])


@main.route('/logout')
def logout():
    if app.userClass.logout():
        flash('You are logged out!', 'success')
    return redirect(url_for('login'))


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
                return redirect(url_for('posts'))
    else:
        if session.get('user'):
            return redirect(url_for('posts'))

    return render_template('login.html',
                           meta_title='Login',
                           error=error,
                           error_type=error_type)


@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method != 'POST':
        return redirect(url_for('index'))

    query = request.form.get('query', None)
    if query:
        return redirect(url_for('search_results', query=query))
    else:
        return redirect(url_for('index'))

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
        if url_for('static', filename='') not in request.path and request.path != url_for('install'):
            if not current_app.settingsClass.is_installed():
                return redirect(url_for('install'))


@main.before_request
def set_globals():
    current_app.jinja_env.globals['csrf_token'] = generate_csrf_token
    current_app.jinja_env.globals['recent_posts'] = app.postClass.get_posts(10, 0)['data']
    current_app.jinja_env.globals['tags'] = app.postClass.get_tags()['data']




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


@main.route('/newpost', methods=['GET', 'POST'])
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

            post = app.postClass.validate_post_data(post_data)
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
                    response = app.postClass.edit_post(
                        request.form['post-id'], post)
                    if not response['error']:
                        flash('Post updated!', 'success')
                    else:
                        flash(response['error'], 'error')
                    return redirect(url_for('posts'))
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
                return redirect(url_for('blog_settings'))

    return render_template('settings.html',
                           default_settings=current_app.config,
                           meta_title='Settings',
                           error=error,
                           error_type=error_type)


@main.route('/manage_trifles')
@login_required()
def manage_trifles():
    return render_template('manage_trifles.html')


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
                     url_for('single_post', permalink=post['permalink'])),
                 updated=post['date'])
    return feed.get_response()
