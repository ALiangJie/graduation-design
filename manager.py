"""
相关配置信息
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
from config import Config

app = Flask(__name__)

# 加载配置类
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

@app.route('/', methods=["POST", "GET"])
def hello_world():
    return "helloworld"


if __name__ == '__main__':
    app.run()
