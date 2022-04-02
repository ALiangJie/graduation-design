from info.models import User, Virus
from info.modules.index import index_blue
from flask import render_template, current_app, session, request, jsonify


# 病毒数据的显示
# 请求路径: /virus_table
# 请求方式: GET
# 请求参数: cid,page,per_page
# 返回值: data数据
@index_blue.route('/virus_list')
def virus_list():
    """
       1. 获取参数,p
       2. 参数类型转换
       3. 分页查询病毒数据
       4. 获取分页对象属性,总页数,当前页,当前页对象列表
       5. 将对象列表,转成字典列表
       6. 拼接数据,渲染页面
       :return:
       """
    # 1. 获取参数,p
    page = request.args.get("p", "1")

    # 2. 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3. 分页查询病毒数据
    try:
        paginate = Virus.query.filter().order_by(Virus.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("virus_list.html")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    virus_list = []
    for virus in items:
        virus_list.append(virus.to_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "virus_list": virus_list
    }
    return render_template("virus_list.html", data=data)


# 主页的用户显示
@index_blue.route('/user_index', methods=["POST", "GET"])
def user_index_show():
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
    return render_template("user_index.html", data=data)


# 用户登录界面显示
@index_blue.route('/', methods=["POST", "GET"])
def user_login_show():
    return render_template("user_login.html")


# 欢迎页面显示
@index_blue.route('/user_welcome', methods=["POST", "GET"])
def user_welcome_index_show():
    return render_template("user_welcome.html")


# 处理网站favicon.ico
@index_blue.route('/favicon.ico')
def get_web_favicon():
    return current_app.send_static_file('images/favicon.ico')


# 处理网站logo
@index_blue.route('/images/logo.png')
def get_web_logo():
    return current_app.send_static_file('images/logo.png')
