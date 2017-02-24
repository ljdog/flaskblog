from flask import Blueprint

mg = Blueprint('mg',__name__)

from . import views, model