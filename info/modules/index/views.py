from info.modules.index import index_blue


# index装饰视图函数
@index_blue.route('/', methods=["POST", "GET"])
def hello_world():
    return "helloworld"
