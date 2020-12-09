from flask import Blueprint


login_blue = Blueprint("login",__name__,url_prefix="/user")
from . import views