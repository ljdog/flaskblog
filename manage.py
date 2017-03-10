# coding:utf-8
from flask_script import Manager

from blog_app.application import create_app
app = create_app()

manager = Manager(app)


if __name__ == '__main__':
    app.debug = True
    manager.run()
