import logging
from datetime import timedelta
from redis import StrictRedis
#设置配置信息
class Config(object):
    #调试信息
    DEBUG = True
    SECRET_KEY = "fdfdjfkdjfkdf"

    #配置mysql数据库信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123@localhost:3306/NBNews"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 自动提交
    #配置redis信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #配置session信息
    SESSION_TYPE = "redis" 
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT) 
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=2) #设置session有效期,两天时间

    #配置日志信息
    module_name = "News"
    logdir = "/home/moluo/Desktop/NBNews/logs"
    log_level = "debug"


#开发环境配置
class DevelopConfig(Config):
    pass

#生产环境配置
class ProductConfig(Config):
    DEBUG = False
    LEVEL_NAME = logging.ERROR
    
#测试环境
class TestConfig(Config):
    pass

#提供统一访问接口
config_dict = {
    "dev" : DevelopConfig,
    "product" : ProductConfig,
    "test" : TestConfig
}
