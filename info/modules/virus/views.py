from flask import jsonify, current_app, render_template, abort, session, g, request

from info import db
from info.commons import user_login_data
from info.models import Virus, Comment, CommentLike
from info.modules.virus import virus_blue
from info.response_code import RET


# 评论点赞
# 请求路径: /virus/comment_like
# 请求方式: POST
# 请求参数:virus_id,comment_id,action,g.user
# 返回值: errno,errmsg
@virus_blue.route('/comment_like', methods=['POST'])
@user_login_data
def comment_like():
    """
    1. 判断用户是否有登陆
    2. 获取参数
    3. 参数校验,为空校验
    4. 操作类型进行校验
    5. 通过评论编号查询评论对象,并判断是否存在
    6. 根据操作类型点赞取消点赞
    7. 返回响应
    :return:
    """
    # 1. 判断用户是否有登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2. 获取参数
    comment_id = request.json.get("comment_id")
    action = request.json.get("action")

    # 3. 参数校验,为空校验
    if not all([comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4. 操作类型进行校验
    if not action in ["add", "remove"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 5. 通过评论编号查询评论对象,并判断是否存在
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    if not comment: return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 6. 根据操作类型点赞取消点赞
    try:
        if action == "add":
            # 6.1 判断用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment_id).first()
            if not comment_like:
                # 创建点赞对象
                comment_like = CommentLike()
                comment_like.user_id = g.user.id
                comment_like.comment_id = comment_id

                # 添加到数据库中
                db.session.add(comment_like)

                # 将该评论的点赞数量+1
                comment.like_count += 1
                db.session.commit()
        else:
            # 6.2 判断用户是否有对该评论点过赞
            comment_like = CommentLike.query.filter(CommentLike.user_id == g.user.id,
                                                    CommentLike.comment_id == comment_id).first()
            if comment_like:
                # 删除点赞对象
                db.session.delete(comment_like)

                # 将该评论的点赞数量1
                if comment.like_count > 0:
                    comment.like_count -= 1
                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="操作失败")

    # 7. 返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 数据评论后端
# 请求路径: /virus/virus_comment
# 请求方式: POST
# 请求参数:virus_id,comment,parent_id, g.user
# 返回值: errno,errmsg,评论字典
@virus_blue.route('/virus_comment', methods=['POST'])
@user_login_data
def virus_comment():
    """
    1. 判断用户是否登陆
    2. 获取请求参数
    3. 校验参数,为空校验
    4. 根据病毒数据编号取出病毒数据对象,判断病毒数据是否存在
    5. 创建评论对象,设置属性
    6. 保存评论对象到数据库中
    7. 返回响应,携带评论的数据
    :return:
    """
    # 1. 判断用户是否登陆
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2. 获取请求参数
    virus_id = request.json.get("virus_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")

    # 3. 校验参数,为空校验
    if not all([virus_id, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4. 根据病毒数据编号取出病毒数据对象,判断病毒数据是否存在
    try:
        virus = Virus.query.get(virus_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取病毒数据失败")

    if not virus: return jsonify(errno=RET.NODATA, errmsg="病毒数据不存在")

    # 5. 创建评论对象,设置属性
    comment = Comment()
    comment.user_id = g.user.id
    comment.virus_id = virus_id
    comment.content = content
    if parent_id:
        comment.parent_id = parent_id

    # 6. 保存评论对象到数据库中
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="评论失败")

    # 7. 返回响应,携带评论的数据
    return jsonify(errno=RET.OK, errmsg="评论成功", data=comment.to_dict())


# 收藏功能接口
# 请求路径: /virus/virus_collect
# 请求方式: POST
# 请求参数:virus_id,action, g.user
# 返回值: errno,errmsg
@virus_blue.route('/virus_collect', methods=['POST'])
@user_login_data
def virus_collect():
    """
    1. 判断用户是否登陆了
    2. 获取参数
    3. 参数校验,为空校验
    4. 操作类型校验
    5. 根据病毒数据的编号取出病毒数据对象
    6. 判断病毒数据对象是否存在
    7. 根据操作类型,进行收藏&取消收藏操作
    8. 返回响应
    :return:
    """
    # 1. 判断用户是否登陆了
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg="用户未登录")

    # 2. 获取参数
    virus_id = request.json.get("virus_id")
    action = request.json.get("action")

    # 3. 参数校验,为空校验
    if not all([virus_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 4. 操作类型校验
    if not action in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.DATAERR, errmsg="操作类型有误")

    # 5. 根据病毒数据的编号取出病毒数据对象
    try:
        virus = Virus.query.get(virus_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="病毒数据获取失败")

    # 6. 判断病毒数据对象是否存在
    if not virus:
        return jsonify(errno=RET.NODATA, errmsg="病毒数据不存在")

    # 7. 根据操作类型,进行收藏&取消收藏操作
    if action == "collect":
        # 7.1 判断用户是否有对该病毒数据做过收藏
        if not virus in g.user.collection_virus:
            g.user.collection_virus.append(virus)
    else:
        # 7.2 判断用户是否有对该病毒数据做过收藏
        if virus in g.user.collection_virus:
            g.user.collection_virus.remove(virus)

    # 8. 返回响应
    return jsonify(errno=RET.OK, errmsg="操作成功")


# 病毒数据详情页
# 请求路径: /virus/<int:virus_id>
# 请求方式: GET
# 请求参数:virus_id
# 返回值: virus_detail.html页面, 用户data字典数据
@virus_blue.route('/<int:virus_id>')
@user_login_data
def virus_detail(virus_id):
    # 1.根据病毒数据编号,查询病毒数据对象
    try:
        virus = Virus.query.get(virus_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取数据失败")

    # 2.如果病毒数据对象不存在直接抛出异常
    if not virus:
        abort(404)

    # 3.判断用户是否收藏
    is_collected = False
    if g.user:
        if virus in g.user.collection_virus:
            is_collected = True
    # 6.查询数据库中,该病毒数据的所有评论内容
    try:
        comments = Comment.query.filter(Comment.virus_id == virus_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取评论失败")

    # 7. 用户点赞过的评论编号
    try:
        # 该用户点过所有的赞
        commentlikes = []
        if g.user:
            commentlikes = CommentLike.query.filter(CommentLike.user_id == g.user.id).all()

        # 获取用户所有点赞过的评论编号
        mylike_comment_ids = []
        for commentLike in commentlikes:
            mylike_comment_ids.append(commentLike.comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取点赞失败")

    # 8.将评论的对象列表, 转成字典列表
    comments_list = []
    for comment in comments:
        # 将评论对象,转字典
        comm_dict = comment.to_dict()

        # 添加is_like记录点赞
        comm_dict["is_like"] = False

        # 判断用户是否有对评论点过赞
        if g.user and comment.id in mylike_comment_ids:
            comm_dict["is_like"] = True

        comments_list.append(comm_dict)

    # 3.携带数据,渲染页面
    data = {
        "virus_info": virus.to_dict(),
        "user_info": g.user.to_dict() if g.user else "",
        "is_collected": is_collected,
        "comments": comments_list
    }
    return render_template("virus_detail.html", data=data)
