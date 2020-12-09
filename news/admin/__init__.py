from flask import Blueprint, request, session, redirect

#创建蓝图
admin_blue = Blueprint("admin", __name__,url_prefix="/admin")

from news.admin import views

# 使用请求钩子， 拦截用户请求，只有管理员才有权限访问主页
@admin_blue.before_request
def before_request():
    print(session.get("is_admin"))
    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            return redirect("/")
