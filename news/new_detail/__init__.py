from flask import Blueprint

detail_blue = Blueprint("news_detail", __name__, url_prefix="/news")
from . import views