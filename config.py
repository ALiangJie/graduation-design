from datetime import timedelta
from redis.client import StrictRedis


# 设置配置信息
class Config(object):
    # 1.调试配置信息
    DEBUG = True
    SECRET_KEY = "efsfsfsfef"

    # 2.数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/infoVirus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=10)


# 开发环境配置信息
class DevelopConfig(Config):
    pass


# 生产(线上)环境配置信息
class ProductConfig(Config):
    DEBUG = False
    # LEVEL_NAME = logging.ERROR


# 测试环境配置信息
class TestConfig(Config):
    pass


# 提供一个统一的访问入口
config_dict = {
    "develop": DevelopConfig,
    "product": ProductConfig,
    "test": TestConfig
}