"""
加载配置文件及其他基本配置文件
"""
import logging
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask import Flask, session
from config.config import config_dict,Config
from config.log import logger


redis_store = None
db = SQLAlchemy()

def create_app(config_name):
    """创建app,加载基本配置"""
    #记录日志
    logfile()

    app = Flask(__name__)
    config = config_dict.get(config_name)
    #加载配置类
    app.config.from_object(config)
    db.init_app(app)
    # 创建redis对象
    global redis_store
    redis_store = StrictRedis(host=config.REDIS_HOST,port=config.REDIS_PORT, decode_responses=True)
    #创建Session对象，读取APP中的session信息
    Session(app) 
    #使用CSRFProtect保护app
    CSRFProtect(app)
    
    #注册蓝图index_blue
    from news.index import index_blue
    app.register_blueprint(index_blue)

    from news.login import login_blue
    app.register_blueprint(login_blue)

    from news.new_detail import detail_blue
    app.register_blueprint(detail_blue)

    from news.info_center import info_center
    app.register_blueprint(info_center)
    
    from news.admin import admin_blue
    app.register_blueprint(admin_blue)



    # 使用请求钩子拦截所有请求，通过在cookie中设置csrf-token
    @app.after_request
    def after_request(resp):
        csrf_token = generate_csrf()
        resp.set_cookie("csrf_token", csrf_token)

        return resp

    return app

def logfile():
    """日志文件记录"""
    
    logger.init(module_name=Config.module_name, log_dir=Config.logdir
                , level=Config.log_level)
