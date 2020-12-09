from news.index import index_blue
from news import redis_store
from flask import render_template, current_app, session, jsonify, request
from news.models import User, News, Category
from utils.response_code import Code


#返回页面index.html
# 首页新闻分类，热点排行
@index_blue.route("/", methods=["GET", "POST"])
def news_index():
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    
    # 查询首页热门新闻，根据点击量，查询前十条信息
    try:
        news = News.query.order_by(News.clicks.desc()).limit(9).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=Code.DBERR, errormsg="获取新闻失败！")

    news_list = []
    for item in news:
        news_list.append(item.to_dict())

    # 查询首页分类数据
    try:
        categorys = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=Code.DBERR, errormsg="获取新闻分类失败！")
    
    category_list = []
    for category in categorys:
        category_list.append(category.to_dict())

    data = {
        "user_info": user.to_dict() if user else "",
        "news_list": news_list,
        "category_list": category_list
    }
    # print(data)
    return render_template("news/index.html", data=data)


# 首页新闻列表数据
#请求路劲/newslist
@index_blue.route("/newslist",methods=["GET"])
def newslist():
    cid = request.args.get("cid","1")
    page = request.args.get("page","1")
    per_page = request.args.get("per_page","10")
    
    try:
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        page = 1
        per_page = 10
    
    # 通过分类ID进行分页查询
    try:

        filters = []
        if cid != "1":
            filters.append(News.category_id == cid)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page, False)

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取新闻失败")

    # 获取到分页对象中的属性,总页数,当前页,当前页的对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    news_list = []
    for news in items:
        news_list.append(news.to_dict())
    return jsonify(errno=Code.OK,errmsg="获取新闻成功",totalPage=totalPage,currentPage=currentPage,newsList=news_list)


@index_blue.route("/favicon.ico")
def get_web_logo():
    return current_app.send_static_file("new/favicon.ico") #send_static_file自动去static中找
