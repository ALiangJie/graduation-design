from info.modules.index import index_blue
from ... import redis_store


# index装饰视图函数
@index_blue.route('/', methods=["POST", "GET"])
def hello_world():
    redis_store.set("name", "laowang")
    print(redis_store.get("name"))
    return "helloworld"
