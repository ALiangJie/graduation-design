from info.commons import user_login_data
from info.models import User, Virus
from info.modules.index import index_blue
from flask import render_template, current_app, session, request, jsonify, g
from info.response_code import RET


# 获取病毒数据收藏列表
# 请求路径: /user/ collection
# 请求方式:GET
# 请求参数:p(页数)
# 返回值: user_collection.html页面
@index_blue.route('/collection')
@user_login_data
def collection():
    """
    1. 获取参数,p
    2. 参数类型转换
    3. 分页查询收藏的病毒数据
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

    # 3. 分页查询收藏的病毒数据
    try:
        paginate = g.user.collection_virus.order_by(Virus.create_time.desc()).paginate(page, 5, False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取病毒数据失败")

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

    return render_template("user_collection.html", data=data)


# 获取/设置用户密码
# 请求路径: /user/pass_info
# 请求方式:GET,POST
# 请求参数:GET无, POST有参数,old_password, virus_password
# 返回值:GET请求: user_pass_info.html页面,data字典数据, POST请求: errno, errmsg
@index_blue.route('/pass_info', methods=['GET', 'POST'])
@user_login_data
def pass_info():
    """
    1. 判断请求方式,如果是get请求
    2. 直接渲染页面
    3. 如果是post请求,获取参数
    4. 校验参数,为空校验
    5. 判断老密码是否正确
    6. 设置新密码
    7. 返回响应
    :return:
    """
    # 1. 判断请求方式,如果是get请求
    if request.method == "GET":
        # 2. 直接渲染页面
        return render_template("user_pass_info.html")

    # 3. 如果是post请求,获取参数
    old_password = request.json.get("old_password")
    user_password = request.json.get("user_password")

    # 4. 校验参数,为空校验
    if not all([old_password, user_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 5. 判断老密码是否正确
    if not g.user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg="老密码错误")

    # 6. 设置新密码
    g.user.password = user_password

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 获取/设置用户基本信息
# 请求路径: /user/base_info
# 请求方式:GET,POST
# 请求参数:POST请求有参数,nick_name,signature,gender
# 返回值:errno,errmsg
@index_blue.route('/base_info', methods=['GET', 'POST'])
@user_login_data
def base_info():
    """
    1. 判断请求方式,如果是get请求
    2. 携带用户数据,渲染页面
    3. 如果是post请求
    4. 获取参数
    5. 校验参数,为空校验
    6. 修改用户的数据
    7. 返回响应
    :return:
    """
    # 1. 判断请求方式,如果是get请求
    if request.method == "GET":
        # 2. 携带用户数据,渲染页面
        return render_template("user_base_info.html", user_info=g.user.to_dict())

    # 3. 如果是post请求
    # 4. 获取参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 5. 校验参数,为空校验
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    if not gender in ["MAN", "WOMAN"]:
        return jsonify(errno=RET.DATAERR, errmsg="性别异常")

    # 6. 修改用户的数据
    g.user.signature = signature
    g.user.nick_name = nick_name
    g.user.gender = gender

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="修改成功")


# 病毒数据的显示
# 请求路径: /virus_table
# 请求方式: GET
# 请求参数: cid,page,per_page,keywords
# 返回值: data数据
@index_blue.route('/virus_list')
@user_login_data
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
    # 1. 获取参数,p,keywords
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords", "")
    # 2. 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3. 分页查询病毒数据
    try:
        # 判断是否带有填写搜索关键字
        filters = []
        if keywords:
            filters.append(Virus.title.contains(keywords))

        paginate = Virus.query.filter(*filters).order_by(Virus.create_time.desc()).paginate(page, 10, False)
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
@user_login_data
def user_index_show():
    # 3.拼接用户数据,渲染页面

    data = {
        # 如果user有值返回左边的内容，否则返回右边的值
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template("user_index.html", data=data)


# 用户登录界面显示
@index_blue.route('/', methods=["POST", "GET"])
def user_login_show():
    return render_template("user_login.html")


# 欢迎页面显示
@index_blue.route('/user_welcome', methods=["GET"])
def user_welcome_index_show():
    return render_template("user_welcome.html")


# 显示首页欢迎界面
@index_blue.route('/welcome_index', methods=["GET"])
def welcome_index_show():
    return render_template("welcome_index.html")


# 显示系统设置界面
@index_blue.route('/setting', methods=["GET"])
def setting_show():
    return render_template("setting.html")


# 处理网站favicon.ico
@index_blue.route('/favicon.ico')
def get_web_favicon():
    return current_app.send_static_file('images/favicon.ico')


# 处理网站logo
@index_blue.route('/images/logo.png')
def get_web_logo():
    return current_app.send_static_file('images/logo.png')
