"""
管理员后台
"""
import time
from datetime import datetime,timedelta
from flask import render_template, request, session, redirect, current_app, g, jsonify
from news.models import User, News, Category
from . import admin_blue
from utils.check_login import check_login
from utils.response_code import Code
from utils.image_storage import image_storage
from news import constants,db


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

# 管理员页面用户列表
@admin_blue.route('/user_list')
def user_list():
    page = request.args.get("p","1")
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 分页查询用户数据
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page,10,False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_list.html",errmsg="获取用户失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "user_list":user_list
    }
    return render_template("admin/user_list.html",data=data)    

# 获取/设置新闻审核列表
@admin_blue.route('/news_review')
def news_review():

    page = request.args.get("p", "1")
    keywords = request.args.get("keywords", "") # 搜索

    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        # 判断是否有填写搜索关键， 进行搜索
        filters = [News.status != 0]
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 3, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_review.html", errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    print(data)
    return render_template("admin/news_review.html", data=data)

# 新闻审核详情
@admin_blue.route('/news_review_detail', methods=['GET', 'POST'])
def news_review_detail():

    if request.method == 'GET':
        # 通过ID去查新闻
        news_id = request.args.get("news_id")
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_review_detail.html",errmsg="新闻获取失败")

        if not news:
            return render_template("admin/news_review_detail.html",errmsg="该新闻不存在")
        return render_template("admin/news_review_detail.html",news=news.to_dict())

    action = request.json.get("action")
    news_id = request.json.get("news_id")

    if not all([news_id,action]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")

    if not action in ["accept","reject"]:
        return jsonify(errno=Code.DATAERR,errmsg="操作类型有误")

    # 通过ID获取新闻并且改变新闻状态
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取新闻失败")

    if not news:
        return jsonify(errno=Code.NODATA, errmsg="该新闻不存在")

    if action == "accept":
        news.status = 0
    else:
        news.status = -1
        news.reason = request.json.get("reason","")


    return jsonify(errno=Code.OK,errmsg="操作成功")

# 新闻版式编辑
@admin_blue.route('/news_edit')
def news_edit():
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords", "")

    try:
        page = int(page)
    except Exception as e:
        page = 1

    #  分页查询待审核,未通过的新闻数据
    try:

        #判断是否有填写搜索关键
        filters = []
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_edit.html", errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "news_list": news_list
    }
    return render_template("admin/news_edit.html", data=data)

# 新闻版式编辑详情页面
@admin_blue.route('/news_edit_detail', methods=['GET', 'POST'])
def news_edit_detail():

    if request.method == "GET":
        news_id = request.args.get("news_id")

        # 判断新闻对象是否存在
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/news_edit_detail.html",errmsg="新闻获取失败")

        if not news:
            return render_template("admin/news_edit_detail.html",errmsg="该新闻不存在")
        # 获取分类
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("",errmsg="分类获取失败")

        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        return render_template("admin/news_edit_detail.html",news=news.to_dict(),category_list=category_list)

    news_id = request.form.get("news_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    if not all([news_id,title,digest,content,category_id]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")

    # 根据ID取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取新闻失败")

    if not news:
        return jsonify(errno=Code.NODATA,errmsg="新闻不存在")

    # 上传新闻图片
    try:
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.THIRDERR,errmsg="七牛云异常")

    if not image_name:
        return jsonify(errno=Code.NODATA,errmsg="图片上传失败")

    news.title = title
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id

    return jsonify(errno=Code.OK,errmsg="编辑成功")

# 新闻分类管理
@admin_blue.route('/news_category')
def news_category():
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/news_type.html",errmsg="获取分类失败")
    return render_template("admin/news_type.html",categories=categories)

# 新闻分类添加/修改
@admin_blue.route('/add_category', methods=['POST'])
def add_category():
 
    category_id = request.json.get("id")
    category_name = request.json.get("name")

    if not category_name:
        return jsonify(errno=Code.PARAMERR,errmsg="分类名称不能为空")

    if category_id: 
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=Code.DBERR,errmsg="获取分类失败")

        if not category:
            return jsonify(errno=Code.NODATA,errmsg="该分类不存在")

        category.name = category_name

    else: #新增
        category = Category(name=category_name)

        #添加分类到数据库中
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR,errmsg="分类新增失败")
    return jsonify(errno=Code.OK,errmsg="操作成功")