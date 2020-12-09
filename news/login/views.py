import re
import random
from datetime import datetime
from flask import request, jsonify, make_response, session, current_app
from . import login_blue
from utils.response_code import Code
from utils.captcha.captcha import captcha
from utils.yuntongxun.sms import CCP
from news import constants, redis_store
from news.models import User
from news import db


#用户登录
#请求路径/user/login
#返回页面index.html
@login_blue.route("/login", methods=["POST"])
def login():
    mobile = request.json.get("mobile")
    password = request.json.get("password")
   
    if not all([mobile, password]):
        return jsonify(error=Code.PARAMERR, error_msg="参数不全")
    
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="获取用户失败")

    if not user:
        return jsonify(errno=Code.NODATA,errmsg="该用户不存在")

    if not user.check_password(password):
        return jsonify(errno=Code.DATAERR,errmsg="密码错误")

    session["user_id"] = user.id    # 保存信息到session中
    user.last_login = datetime.now() # 记录登录时间
    # try:
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)
    return jsonify(errno=Code.OK,errmsg="登陆成功")

# 用户注册
#请求路劲 /user/register
@login_blue.route("/register",methods=["GET","POST"])
def register():
    mobile = request.json.get("mobile")
    sms_code = request.json.get("sms_code")
    password = request.json.get("password")
    
    if not all([mobile,sms_code,password]):
        return jsonify(errno=Code.PARAMERR,errmsg="参数不全")

    try:    # 校验短信验证码
        redis_sms_code = redis_store.get("sms_code:%s" %mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="短信验证码取出失败")

    if not redis_sms_code:
        return jsonify(errno=Code.NODATA,errmsg="短信验证码已经过期")

    if sms_code != redis_sms_code:
        return jsonify(errno=Code.DATAERR,errmsg="短信验证码填写错误")

    try:    # 删除短信验证码
        redis_store.delete("sms_code:%s"%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR, errmsg="短信验证码删除失败")

    try:  # 检验该用户是否已经注册过
        user = User.query.filter(User.mobile==mobile).first()
        if user:
            return jsonify(errno=Code.DBERR,errmsg="该用户已存在！")   
    except Exception as e:
        pass
 
    user = User()
    user.nick_name = mobile
    user.password = password  # sha256加密算法
    user.mobile = mobile
    user.signature = "该用户很懒,什么都没写"

    try:    # 保存到数据库
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="用户注册失败")
    return jsonify(errno=Code.OK,errmsg="注册成功")

# 退出
# 请求路劲/user/logout
@login_blue.route("/logout", methods=["POST"])
def logout():
    session["user_id"] = ""
    session["is_admin"] = ""
    return jsonify(error=Code.OK, errmsg="退出成功！")

# 图片验证码
#请求路径/user/image_code   前端操作方法在main.js中
@login_blue.route("/image_code")
def image_code():
    cur_id = request.args.get("cur_id")
    pre_id = request.args.get("pre_id")
    name, text, image_data = captcha.generate_captcha()
    try:
        # 参数1：key, 参数2：value, 参数3：有效期
        redis_store.set("image_code:%s" %cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id: # 去重
            redis_store.delete("image_code:%s" %pre_id)
        print(redis_store.get("image_code:%s" %cur_id))
    except Exception as e:
        current_app.logger.error(e)
    
    response = make_response(image_data)
    response.headers["Content-Type"] = "image/png"
    return response

# 短信验证码
#请求路径/user/sms_code
@login_blue.route("/sms_code", methods=["POST"])
def sms_code():
    mobile = request.json.get("mobile")
    image_code = request.json.get("image_code")
    image_code_id = request.json.get("image_code_id")
    print(mobile, image_code, image_code_id)
    if not all([mobile, image_code, image_code_id]):
        return jsonify(error=Code.PARAMERR, msg="参数不全")
    
    if not re.match("1[3-9]\d{9}",mobile):  #校验手机号
        return jsonify(errno=Code.DATAERR,errmsg="手机号的格式错误")

    try:
        redis_image_code = redis_store.get("image_code:%s"%image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="操作redis失败")

    if not redis_image_code:    
        return jsonify(errno=Code.NODATA,errmsg="图片验证码已经过期")
    
    if image_code.upper() != redis_image_code.upper():  #校验验证码
        return jsonify(errno=Code.DATAERR,errmsg="图片验证码填写错误")

    try:
        redis_store.delete("image_code:%s" % image_code_id)     # 删除验证码
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="删除redis图片验证码失败")
    
    sms_code = "%06d"%random.randint(0,999999)      #生成短信验证码
    current_app.logger.debug("短信验证码是 = %s"%sms_code)
    try:
        redis_store.set("sms_code:%s" % mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=Code.DBERR,errmsg="图片验证码保存到redis失败")
    
    # 发送短信
    # ccp = CCP()
    # result = ccp.send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],1)
    # if result == -1:
    #     return jsonify(errno=Code.ODATAERR,errmsg="短信发送失败")
    print(mobile, image_code, image_code_id, sms_code)
    return jsonify(errno=Code.OK,errmsg="短信发送成功")
    
