from info.modules.index import index_blue
from flask import render_template, current_app


# index装饰视图函数
@index_blue.route('/', methods=["POST", "GET"])
def index_show():
    return render_template("user/index.html")


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('img/favicon.ico')
