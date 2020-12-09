from flask import Blueprint


info_center = Blueprint("info_center",__name__,url_prefix="/info_center")
from . import views