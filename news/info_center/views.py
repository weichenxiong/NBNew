"""
个人中心设置
"""
from . import info_center
from flask import render_template, current_app, session, jsonify, request, g, redirect
from news.models import User, News, Category
from utils.check_login import check_login
from utils.response_code import Code
from utils.image_storage import image_storage
from news import constants,db


# 获取用户首页基本信息
#返回user_center.html，用户个人中心首页
@info_center.route("/user_index")
@check_login
def user_index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    data = {
        "user_info": user.to_dict() if user else "",
    }
    return render_template("news/user_center.html", data=data)


# 获取/设置用户基本资料
@info_center.route("/base_info", methods=["GET", "POST"])
@check_login
def base_info():
    if request.method == "GET":
        return render_template("news/user_base_info.html", user_info=g.user.to_dict() if g.user else "")
    
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name,signature,gender]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")
    
    if not gender in ["MAN","WOMAN"]:
        return jsonify(errno=Code.DATAERR,errmsg="性别异常")
    
    # g.user里面封装了USer
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    return jsonify(errno=Code.OK,errmsg="修改成功")

# 获取/设置上传头像设置
@info_center.route("/pic_info", methods=["GET", "POST"])
@check_login
def pic_info():
    if request.method == "GET":
        # 携带用户的数据,渲染页面
        print(g.user.to_dict())
        return render_template("news/user_pic_info.html",user_info=g.user.to_dict())
    
    # 获取头像图片参数
    avatar = request.files.get("avatar")
    if not avatar:
        return jsonify(errno=Code.PARAMERR,errmsg="图片不能为空")
    
    # 图片上传到七牛云
    try:
        image_name =  image_storage(avatar.read())

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.THIRDERR,errmsg="七牛云异常")

    if not image_name:
        return jsonify(errno=Code.NODATA,errmsg="图片上传失败")

    g.user.avatar_url = image_name
    # 返回七牛云存储图片的完整连接
    data = {
        "avatar_url":constants.QINIU_DOMIN_PREFIX + image_name
    }
    print("上传图片成功")
    return jsonify(errno=Code.OK,errmsg="上传成功",data=data)
    

#修改密码
@info_center.route("/password_info", methods=["GET", "POST"])
@check_login
def set_password():
    if request.method == "GET":
        return render_template("news/user_pass_info.html")

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password,new_password]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")

    if not g.user.check_password(old_password):
        return jsonify(errno=Code.DATAERR,errmsg="旧密码错误")
    
    g.user.password = new_password
    return jsonify(errno=Code.OK,errmsg="修改成功")

#新闻发布
@info_center.route("/news_release", methods=["GET", "POST"])
@check_login
def news_release():
    #进行页面渲染
    if request.method == "GET":
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=Code.DBERR,errmsg="获取分类失败")
            
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        return render_template("news/user_news_release.html",categories=category_list)

    # 数据提交
    title = request.form.get("title")
    category_id = request.form.get("category_id")
    digest = request.form.get("digest")
    index_image = request.files.get("index_image")
    content = request.form.get("content")

    if not all([title,category_id,digest,index_image,content]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")
    
    try:
        #读取图片为二进制数据,上传
        image_name = image_storage(index_image.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.THIRDERR,errmsg="七牛云异常")
    
    if not image_name:
        return jsonify(errno=Code.NODATA,errmsg="图片上传失败")
    
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest  = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.category_id = category_id
    news.user_id = g.user.id
    news.status = 1 #表示审核中

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="新闻发布失败")
    # print("发布成功")
    return jsonify(errno=Code.OK,errmsg="发布成功")

# 获取新闻列表
@info_center.route('/news_list')
@check_login
def get_new_list():
    page = request.args.get("p","1")
    try:
        page = int(page)
    except Exception as e:
        page = 1

    try:
        paginate = News.query.filter(News.user_id == g.user.id).order_by(News.create_time.desc()).paginate(page,3,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="获取新闻失败")

    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_review_dict())

    data = {
        "totalPage":totalPage,
        "currentPage":currentPage,
        "news_list":news_list
    }
    return render_template("news/user_news_list.html",data=data)

