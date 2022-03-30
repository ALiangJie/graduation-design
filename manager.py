"""
相关配置信息
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from datetime import timedelta

from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)


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


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建Redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)

# 创建Session对象,读取App中Session配置信息
Session(app)

# 使用CSRFProtect保护app，验证机制，防止CSRF攻击，['POST', 'PUT', 'PATCH', 'DELETE']
CSRFProtect(app)


# 测试redis存取数据
# redis_store.set("name", "laowang")
# print(redis_store.get("name"))


# 测试Session存取数据
# session["name"] = "zhangsan"
# print(session.get("name"))

@app.route('/')
def hello_world():
    return "helloworld"


if __name__ == '__main__':
    app.run()
