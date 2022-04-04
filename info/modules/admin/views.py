from flask import render_template, request, current_app, g, jsonify, redirect, session
import time
from datetime import datetime, timedelta
from info.response_code import RET
from info import constants, db
from info.commons import user_login_data
from info.models import User, Virus, Category
from info.modules.admin import admin_blue


# 获取/设置病毒数据编辑详情
# 请求路径: /admin/virus_edit_detail
# 请求方式: GET, POST
# 请求参数: GET, virus_id, POST(virus_id,title,digest,content,index_image,category_id)
# 返回值:GET,渲染virus_edit_detail.html页面,data字典数据, POST(errno,errmsg)
@admin_blue.route('/virus_edit_detail', methods=['GET', 'POST'])
def virus_edit_detail():
    """
    1.判断请求方式,如果是GET
    2.获取病毒数据编号
    3.通过病毒数据编号查询病毒数据对象,并判断病毒数据对象是否存在
    4.携带病毒数据数据和分类数据,渲染页面
    5.如果是POST请求,获取参数
    6.参数校验,为空校验
    7.根据病毒数据的编号取出病毒数据对象
    8.上传病毒数据图片
    9.设置病毒数据对象的属性
    10.返回响应
    :return:
    """
    # 1.判断请求方式,如果是GET
    if request.method == "GET":
        # 2.获取病毒数据编号
        virus_id = request.args.get("virus_id")

        # 3.通过病毒数据编号查询病毒数据对象,并判断病毒数据对象是否存在
        try:
            virus = Virus.query.get(virus_id)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("admin/virus_edit_detail.html", errmsg="病毒数据获取失败")

        if not virus:
            return render_template("admin/virus_edit_detail.html", errmsg="该病毒数据不存在")

        # 3.1获取分类数据
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
            return render_template("", errmsg="分类获取失败")

        # 3.2将分类对象列表数据,转成字典数据
        category_list = []
        for category in categories:
            category_list.append(category.to_dict())

        # 4.携带病毒数据数据和分类数据, 渲染页面
        return render_template("admin/virus_edit_detail.html", virus=virus.to_dict(), category_list=category_list)

    # 5.如果是POST请求,获取参数(virus_id,title,digest,content,index_image,category_id)
    virus_id = request.form.get("virus_id")
    title = request.form.get("title")
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")

    # 6.参数校验,为空校验
    if not all([virus_id, title, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 7.根据病毒数据的编号取出病毒数据对象
    try:
        virus = Virus.query.get(virus_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取病毒数据失败")

    if not virus:
        return jsonify(errno=RET.NODATA, errmsg="病毒数据不存在")

    # 9.设置病毒数据对象的属性
    virus.title = title
    virus.digest = digest
    virus.content = content
    virus.category_id = category_id

    # 10.返回响应
    return jsonify(errno=RET.OK, errmsg="编辑成功")


# 病毒数据版式编辑
# 请求路径: /admin/virus_edit
# 请求方式: GET
# 请求参数: GET, p, keywords
# 返回值:GET,渲染virus_edit.html页面,data字典数据
@admin_blue.route('/virus_edit')
def virus_edit():
    """
      1. 获取参数,p,keywords
      2. 参数类型转换
      3. 分页查询用户数据
      4. 获取分页对象属性,总页数,当前页,当前页对象列表
      5. 将对象列表,转成字典列表
      6. 拼接数据,渲染页面
      :return:
      """
    # 1. 获取参数,p
    page = request.args.get("p", "1")
    keywords = request.args.get("keywords", "")

    # 2. 参数类型转换
    try:
        page = int(page)
    except Exception as e:
        page = 1

    # 3. 分页查询待审核,未通过的病毒数据数据
    try:

        # 3.1判断是否有填写搜索关键
        filters = []
        if keywords:
            filters.append(Virus.title.contains(keywords))

        paginate = Virus.query.filter(*filters).order_by(Virus.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/virus_edit.html", errmsg="获取病毒数据失败")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    virus_list = []
    for virus in items:
        virus_list.append(virus.to_review_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "virus_list": virus_list
    }
    return render_template("admin/virus_edit.html", data=data)


# 用户列表
# 请求路径: /admin/user_list
# 请求方式: GET
# 请求参数: p
# 返回值:渲染user_list.html页面,data字典数据
@admin_blue.route('/user_list')
def user_list():
    """
    1. 获取参数,p
    2. 参数类型转换
    3. 分页查询用户数据
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

    # 3. 分页查询用户数据
    try:
        paginate = User.query.filter(User.is_admin == False).order_by(User.create_time.desc()).paginate(page, 10, False)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_list.html", errmsg="获取用户失败")

    # 4. 获取分页对象属性,总页数,当前页,当前页对象列表
    totalPage = paginate.pages
    currentPage = paginate.page
    items = paginate.items

    # 5. 将对象列表,转成字典列表
    user_list = []
    for user in items:
        user_list.append(user.to_admin_dict())

    # 6. 拼接数据,渲染页面
    data = {
        "totalPage": totalPage,
        "currentPage": currentPage,
        "user_list": user_list
    }
    return render_template("admin/user_list.html", data=data)


# 用户可视化统计
# 请求路径: /admin/user_count
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面user_count.html,字典数据
@admin_blue.route('/user_count')
def user_count():
    # 1.获取用户总数
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取总人数失败")

    # 2.获取月活人数
    localtime = time.localtime()
    try:
        # 2.1先获取本月的1号的0点的, 字符串数据
        month_start_time_str = "%s-%s-01" % (localtime.tm_year, localtime.tm_mon)

        # 2.2根据字符串,格式化日期对象
        month_start_time_date = datetime.strptime(month_start_time_str, "%Y-%m-%d")

        # 2.3最后一次登陆的时间大于,本月的1号的0点钟的人数
        month_count = User.query.filter(User.last_login >= month_start_time_date, User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取月活人数失败")

    # 3.获取日活人数
    try:
        # 2.1先获取本日的0点, 字符串数据
        day_start_time_str = "%s-%s-%s" % (localtime.tm_year, localtime.tm_mon, localtime.tm_mday)

        # 2.2根据字符串,格式化日期对象
        day_start_time_date = datetime.strptime(day_start_time_str, "%Y-%m-%d")

        # 2.3最后一次登陆的时间大于,本日0点钟的人数
        day_count = User.query.filter(User.last_login >= day_start_time_date, User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/user_count.html", errmsg="获取日活人数失败")

    # 4.获取活跃时间段内,对应的活跃人数
    active_date = []  # 获取活跃的日期
    active_count = []  # 获取活跃的人数
    for i in range(0, 31):
        # 当天开始时间A
        begin_date = day_start_time_date - timedelta(days=i)
        # 当天开始时间, 的后⼀一天B 
        end_date = day_start_time_date - timedelta(days=i - 1)
        # 添加当天开始时间字符串串到, 活跃⽇日期中
        active_date.append(begin_date.strftime("%Y-%m-%d"))
        # 查询时间A到B这⼀一天的注册⼈人数
        everyday_active_count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                                  User.last_login <= end_date).count()
        # 添加当天注册⼈人数到,获取数量量中
        active_count.append(everyday_active_count)

    # 为了图表显示方便,将容器反转
    active_count.reverse()
    active_date.reverse()

    # 5.携带数据渲染页面
    data = {
        "total_count": total_count,
        "month_count": month_count,
        "day_count": day_count,
        "active_date": active_date,
        "active_count": active_count
    }
    return render_template("admin/user_count.html", data=data)


# 管理员首页
# 请求路径: /admin/index
# 请求方式: GET
# 请求参数: 无
# 返回值:渲染页面index.html,user字典数据
@admin_blue.route('/index')
@user_login_data
def admin_index():
    data = {
        "user_info": g.user.to_dict() if g.user else ""
    }
    return render_template("admin/index.html", data=data)


# 退出登陆
# 请求路径: /passport/logout
# 请求方式: POST
# 请求参数: 无
# 返回值: errno, errmsg
@admin_blue.route('/logout', methods=['POST'])
def admin_logout():
    """
    1.清除session信息
    2.返回响应
    :return:
    """
    # 1.清除session信息
    session.pop("user_id", None)
    session.pop("is_admin", None)

    # 2.返回响应
    return jsonify(errno=RET.OK, errmsg="退出成功")


# 获取/登陆,管理员登陆
# 请求路径: /admin/login
# 请求方式: GET,POST
# 请求参数:GET,无, POST,username,password
# 返回值: GET渲染login.html页面, POST,login.html页面,errmsg
@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    """
    1.判断请求方式,如果是GET,直接渲染页面
    2.如果是POST请求,获取参数
    3.校验参数,为空校验
    4.根据用户名取出管理员对象,判断管理员是否存在
    5.判断管理员的密码是否正确
    7.重定向到首页展示
    :return:
    """
    # 1.判断请求方式,如果是GET,直接渲染页面
    if request.method == "GET":
        return render_template("admin/login.html")

    # 2.如果是POST请求,获取参数
    username = request.form.get("username")
    password = request.form.get("password")

    # 3.校验参数,为空校验
    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数不全")

    # 4.根据用户名取出管理员对象,判断管理员是否存在
    try:
        admin = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template("admin/login.html", errmsg="用户查询失败")

    if not admin:
        return render_template("admin/login.html", errmsg="管理员不存在")

    # 5.判断管理员的密码是否正确
    if not admin.check_password(password):
        return render_template("admin/login.html", errmsg="密码错误")

    # 6.管理的session信息记录
    session["user_id"] = admin.id
    session["is_admin"] = True

    # 7.重定向到首页展示
    return redirect("/admin/index")
