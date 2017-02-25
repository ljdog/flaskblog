# coding:utf-8
from flask_script import Manager

from app import create_app

apps = create_app()
manager = Manager(apps)
if __name__ == '__main__':
    apps.debug = True
    manager.run()
