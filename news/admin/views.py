import time
from datetime import datetime,timedelta
from flask import render_template, request, session, redirect, current_app, g
from news.models import User
from . import admin_blue
from utils.check_login import check_login


# 后台管理页面登录
@admin_blue.route("/login", methods=["GET", "POST"])
@check_login
def admin_login():

    if request.method == "GET":
        # if session.get("is_admin"):
        #     return redirect("admin/index")
        return render_template("admin/login.html")    

    username = request.form.get("username")
    password = request.form.get("password")
    
    if not all([username,password]):
        return render_template("admin/login.html",errmsg="参数不全")
 
    try:
        admin = User.query.filter(User.mobile==username, User.is_admin==True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户信息错误！")
 
    if not admin:
        return render_template("admin/login.html", errmsg="账号不存在！")
    
    if not admin.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误！")
    
    session["user_id"] = admin.id
    session["is_admin"] = True
    return redirect("/admin/index")


# 后台管理首页渲染
@admin_blue.route("/index", methods=["GET", "POST"])
@check_login
def admin_index():
    data = {
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template("admin/index.html", data=data)

# 后台管理页面的用户统计
@admin_blue.route("/user_count", methods=["GET", "POST"])
@check_login
def user_count():
   # 获取用户总数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html",errmsg="获取总人数失败")

    # 获取月活人数
    localtime = time.localtime()
    try:
        month_start_time_str = "%s-%s-01"%(localtime.tm_year,localtime.tm_mon)
        month_start_time_date = datetime.strptime(month_start_time_str,"%Y-%m-%d")
        month_count = User.query.filter(User.last_login >= month_start_time_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取月活人数失败")

    # 获取日活人数
    try:
        day_start_time_str = "%s-%s-%s" % (localtime.tm_year, localtime.tm_mon,localtime.tm_mday)
        day_start_time_date = datetime.strptime(day_start_time_str, "%Y-%m-%d")
        day_count = User.query.filter(User.last_login >= day_start_time_date,User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取日活人数失败")

    active_date = []  # 获取活跃的日期
    active_count = []  # 获取活跃的人数
    for i in range(0,31):
        
        begin_date = day_start_time_date - timedelta(days=i) # 当天开始时间
        end_date = day_start_time_date - timedelta(days=i - 1) # 当天结束时间
        active_date.append(begin_date.strftime("%Y-%m-%d"))
        everyday_active_count = User.query.filter(User.is_admin == False,User.last_login >=begin_date,User.last_login<=end_date).count()
        active_count.append(everyday_active_count)

    active_count.reverse()
    active_date.reverse()
    data = {
        "total_count":total_count,
        "month_count":month_count,
        "day_count":day_count,
        "active_date":active_date,
        "active_count":active_count
    }
    return render_template("admin/user_count.html",data=data)