from . import detail_blue
from news.models import News, User, Comment
from utils.response_code import Code
from utils.check_login import check_login
from flask import render_template, current_app, session, jsonify, request, abort, g
from news import db
#新闻详情
#请求路径/news/<int:new_id>
# 返回页面  detail.html
@detail_blue.route("/<int:new_id>")
@check_login
def news_detail(new_id):
    #取user_id, 用户登录状态
    user_id = session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    
    # 根据ID获取新闻内容
    try:
        new_content = News.query.get(new_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(error=Code.DBERR, errormsg="获取新闻详情失败！")

    if not new_content:
        abort(404)

    #获取热门新闻点击排行
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)

    click_news_list = []
    for item_news in click_news:
        click_news_list.append(item_news.to_dict())

    #判断用户是否收藏过该新闻
    is_collected = False
    #用户需要登陆,并且该新闻在用户收藏过的新闻列表中
    if g.user:
        if click_news in g.user.collection_news:
            is_collected = True

    #所有评论内容
    try:
        comments = Comment.query.filter(Comment.news_id == new_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取评论失败")

    comments_list = []
    for comment in comments:
        comments_list.append(comment.to_dict())

    data = {
        "user_info": user.to_dict() if user else "" , # 用户
        "news_info": new_content.to_dict() if new_content else "" , # 新闻内容详情
        "news_list" : click_news_list, # 热点新闻排行
        "is_collected":is_collected, # 收藏
        "comments":comments_list # 评论信息
    }

    return render_template("news/detail.html", data=data)


# 文章评论
@detail_blue.route('/news_comment', methods=['POST'])
@check_login
def news_comment():
 
    if not g.user:  #判断用户是否登录
        return jsonify(errno=Code.NODATA,errmsg="用户未登录!")
    
    news_id  = request.json.get("news_id")
    content  = request.json.get("comment")
    parent_id  = request.json.get("parent_id")
    print(news_id, content)
    if not all([news_id,content]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")
    
    # 取出新闻对象
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取新闻失败")
    
    if not news: return jsonify(errno=Code.NODATA,errmsg="新闻不存在")

    # 创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.news_id = news_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id
    # 保存评论
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="评论失败")
    print() 
    return jsonify(errno=Code.OK,errmsg="评论成功",data=comment.to_dict())