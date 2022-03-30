"""
相关配置信息
1.数据库配置
2.redis配置
3.session配置
4.csrf配置
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


# 设置配置信息
class Config(object):
    # 调试信息
    DEBUG = True

    # 数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@localhost:3306/infoVirus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


app.config.from_object(Config)

# 创建SQLAlchemy对象，关联app
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    return "helloworld"

if __name__ == '__main__':
    app.run()