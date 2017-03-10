from flask import Blueprint

bp = Blueprint('mg', __name__)

from . import views, model
