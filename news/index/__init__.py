from flask import Blueprint

#创建蓝图
index_blue = Blueprint("index", __name__)

from news.index import views
