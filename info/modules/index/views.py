from info.models import User
from info.modules.index import index_blue
from flask import render_template, current_app, session


# 主界面的用户显示
@index_blue.route('/', methods=["POST", "GET"])
def index_show():
    # 1.获取用户的登录信息
    user_id = session.get("user_id")

    # 2.通过user_id取出用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 3.拼接用户数据,渲染页面

    data = {
        # 如果user有值返回左边的内容，否则返回右边的值
        "user_info": user.to_dict() if user else ""
    }

    return render_template("user/index.html", data=data)


# 处理网站logo
@index_blue.route('/favicon.ico')
def get_web_logo():
    return current_app.send_static_file('img/favicon.ico')
