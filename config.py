"""
相关配置信息
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
import logging
from datetime import timedelta
from redis.client import StrictRedis


# 设置配置信息
class Config(object):
    # 1.调试配置信息
    DEBUG = True
    SECRET_KEY = "dwafadwagtrstgrfd"

    # 2.数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/infoVirus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True  # 每当改变数据的内容之后，在视图函数结束时都会自动提交

    # 3.Redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # 4.Session配置信息
    # 4.1设置Session存储类型
    SESSION_TYPE = "redis"
    # 4.2指定session存储的redis服务器
    SESSION_PERMANENT = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 4.3设置签名存储
    SESSION_USE_SIGNER = True
    # 4.4设置session有效期
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=240000)

    # 5.默认日志级别
    LEVEL_NAME = logging.DEBUG


# 开发环境配置信息
class DevelopConfig(Config):
    pass


# 生产(线上)环境配置信息
class ProductConfig(Config):
    DEBUG = False
    LEVEL_NAME = logging.ERROR


# 测试环境配置信息
class TestConfig(Config):
    pass


# 提供一个统一的访问入口
config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestConfig
}
