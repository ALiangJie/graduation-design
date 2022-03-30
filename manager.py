"""
相关配置信息
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis

app = Flask(__name__)


# 设置配置信息
class Config(object):
    # 调试信息
    DEBUG = True

    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/infoVirus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

# 创建Redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, decode_responses=True)


@app.route('/')
def hello_world():

    # 测试redis存取数据
    redis_store.set("name","laowang")
    print(redis_store.get("name"))
    return "helloworld"


if __name__ == '__main__':
    app.run()
