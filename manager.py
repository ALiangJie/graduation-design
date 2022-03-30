from info import create_app

# 调用方法，获取app
app = create_app("develop")

if __name__ == '__main__':
    app.run()
