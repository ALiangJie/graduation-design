from flask import Blueprint

# 1.创建蓝图对象
virus_blue = Blueprint("virus", __name__, url_prefix="/virus")

# 2.导入views文件装饰视图函数
from info.modules.virus import views
