from flask import jsonify, current_app, render_template, abort

from info.models import Virus
from info.modules.virus import virus_blue
from info.response_code import RET


# 病毒数据详情页
# 请求路径: /virus/<int:virus_id>
# 请求方式: GET
# 请求参数:virus_id
# 返回值: virus_detail.html页面, 用户data字典数据
@virus_blue.route('/<int:virus_id>')
def virus_detail(virus_id):
    # 1.根据新闻编号,查询新闻对象
    try:
        virus = Virus.query.get(virus_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取新闻失败")

    # 2.如果新闻对象不存在直接抛出异常
    if not virus:
        abort(404)

    # 2.携带数据,渲染页面
    data = {
        "virus_info": virus.to_dict()
    }
    return render_template("virus_detail.html", data=data)
