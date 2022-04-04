from flask import Blueprint, request, session, redirect

# 1.创建管理员蓝图对象
admin_blue = Blueprint("admin", __name__, url_prefix="/admin")

# 2.装饰视图函数
from . import views


# 使用请求钩子,拦截用户的请求,只有访问了admin_blue,所装饰的视图函数需要拦截
# 1.拦截的是访问了非登陆页面
# 2.拦截的是普通用户
@admin_blue.before_request
def before_request():
    # 1.判断访问的是否是非登陆页面
    """
    if request.url.endswith("/admin/login"):
        pass
    else:
        #2.判断是否是管理员
        if session.get("is_admin"):
            pass
        else:
            return redirect("/")
    """

    # 改装上面的代码
    if not request.url.endswith("/admin/login"):
        if not session.get("is_admin"):
            return redirect("/admin/login")
