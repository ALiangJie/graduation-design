from flask import Blueprint

# 1.创建蓝图对象
passport_blue = Blueprint("passport", __name__, url_prefix="/passport")

# 2.导入views文件装饰视图函数
from info.modules.passport import views
