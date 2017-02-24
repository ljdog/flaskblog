from . import main
from flask import request, url_for, render_template,flash,redirect,session
from post import Post
from manage import app
from app.share.helper_functions import make_external
from pagination import Pagination
from user import User
from app.share.helper_functions import login_required

postClass = Post(app.config)
userClass = User(app.config)

@main.route('/', defaults={'page': 1})
@main.route('/page-<int:page>')
def index(page):
    skip = (page - 1) * int(app.config['PER_PAGE'])
    posts = postClass.get_posts(int(app.config['PER_PAGE']), skip)
    count = postClass.get_total_count()
    pag = Pagination(page, app.config['PER_PAGE'], count)
    return render_template('index.html', posts=posts['data'], pagination=pag, meta_title=app.config['BLOG_TITLE'])

@main.route('/logout')
def logout():
    if userClass.logout():
        flash('You are logged out!', 'success')
    return redirect(url_for('login'))


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

@app.route('/users')
@login_required()
def users_list():
    users = userClass.get_users()
    return render_template('users.html', users=users['data'], meta_title='Users')

# @app.route('/posts_list', defaults={'page': 1})
# @app.route('/posts_list/page-<int:page>')
# @login_required()
# def posts(page):
#     session.pop('post-preview', None)
#     skip = (page - 1) * int(app.config['PER_PAGE'])
#     posts = postClass.get_posts(int(app.config['PER_PAGE']), skip)
#     count = postClass.get_total_count()
#     pag = pagination.Pagination(page, app.config['PER_PAGE'], count)
#
#     if not posts['data']:
#         abort(404)
#
#     return render_template('posts.html', posts=posts['data'], pagination=pag, meta_title='Posts')
#

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