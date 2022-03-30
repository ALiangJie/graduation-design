from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from info import constants
from . import db


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""
    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间


# 用户收藏表，建立用户与其收藏病毒数据多对多的关系
tb_user_collection = db.Table(
    "info_user_collection",
    db.Column("user_id", db.Integer, db.ForeignKey("info_user.id"), primary_key=True),  # 用户id
    db.Column("virus_id", db.Integer, db.ForeignKey("info_virus.id"), primary_key=True),  # 病毒数据id
    db.Column("create_time", db.DateTime, default=datetime.now)  # 收藏创建时间
)

# 用户粉丝表
tb_user_follows = db.Table(
    "info_user_fans",
    db.Column('follower_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True),  # 粉丝id
    db.Column('followed_id', db.Integer, db.ForeignKey('info_user.id'), primary_key=True)  # 被跟随的人的id
)


# 用户类
class User(BaseModel, db.Model):
    """用户"""
    __tablename__ = "info_user"

    id = db.Column(db.Integer, primary_key=True)  # 用户id
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录时间
    is_admin = db.Column(db.Boolean, default=False)  # 是否为管理员，默认否
    signature = db.Column(db.String(512))  # 用户签名
    gender = db.Column(db.Enum("MAN", "WOMAN"), default="MAN")  # 性别默认男

    # 当前用户收藏的所有病毒数据
    collection_virus = db.relationship("Virus", secondary=tb_user_collection, lazy="dynamic")  # 用户收藏的病毒数据
    # 用户所有的粉丝，添加了反向引用followed，代表用户都关注了哪些人
    followers = db.relationship('User',
                                secondary=tb_user_follows,
                                primaryjoin=id == tb_user_follows.c.followed_id,
                                secondaryjoin=id == tb_user_follows.c.follower_id,
                                backref=db.backref('followed', lazy='dynamic'),
                                lazy='dynamic')

    # 密码加密处理
    @property
    def password(self):
        raise AttributeError("当前属性不可读")

    @password.setter
    def password(self, value):
        self.password_hash = generate_password_hash(value)

    def check_passowrd(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "mobile": self.mobile,
            "gender": self.gender if self.gender else "MAN",
            "signature": self.signature if self.signature else "",
            "followers_count": self.followers.count,
        }
        return resp_dict

    def to_admin_dict(self):
        resp_dict = {
            "id": self.id,
            "nick_name": self.nick_name,
            "mobile": self.mobile,
            "register": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": self.last_login.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict


# 病毒数据类
class Virus(BaseModel, db.Model):
    """病毒数据"""
    __tablename__ = "info_virus"

    id = db.Column(db.Integer, primary_key=True)  # 数据id
    title = db.Column(db.String(256), nullable=False)  # 数据标题
    source = db.Column(db.String(64), nullable=False)  # 数据来源
    content = db.Column(db.Text, nullable=False)  # 数据内容
    category_id = db.Column(db.Integer, db.ForeignKey("info_category.id"))  # 数据分类
    # 当前数据的所有评论
    comments = db.relationship("Comment", lazy="dynamic")

    def to_review_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict

    def to_basic_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return resp_dict

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "comments_count": self.comments.count(),
            "category": self.category.to_dict(),
        }
        return resp_dict


# 评论类
class Comment(BaseModel, db.Model):
    """评论"""
    __tablename__ = "info_comment"

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    user_id = db.Column(db.Integer, db.ForeignKey("info_user.id"), nullable=False)  # 用户id
    virus_id = db.Column(db.Integer, db.ForeignKey("info_virus.id"), nullable=False)  # 病毒数据id
    content = db.Column(db.Text, nullable=False)  # 评论内容
    parent_id = db.Column(db.Integer, db.ForeignKey("info_comment.id"))  # 父评论id
    parent = db.relationship("Comment", remote_side=[id])  # 自关联
    like_count = db.Column(db.Integer, default=0)  # 点赞条数

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "content": self.content,
            "parent": self.parent.to_dict() if self.parent else None,
            "user": User.query.get(self.user_id).to_dict(),
            "virus_id": self.virus_id,
            "like_count": self.like_count
        }
        return resp_dict


# 评论点赞类
class CommentLike(BaseModel, db.Model):
    """评论点赞"""
    __tablename__ = "info_comment_like"
    comment_id = db.Column("comment_id", db.Integer, db.ForeignKey("info_comment.id"), primary_key=True)  # 评论编号
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("info_user.id"), primary_key=True)  # 用户编号


# 病毒数据分类
class Category(BaseModel, db.Model):
    """病毒数据分类"""
    __tablename__ = "info_category"

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    name = db.Column(db.String(64), nullable=False)  # 分类名
    virus_list = db.relationship('Virus', backref='category', lazy='dynamic')

    def to_dict(self):
        resp_dict = {
            "id": self.id,
            "name": self.name
        }
        return resp_dict
