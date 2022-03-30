from info import create_app

# 调用方法，获取app
app = create_app("develop")


@app.route('/', methods=["POST", "GET"])
def hello_world():
    return "helloworld"


if __name__ == '__main__':
    app.run()
