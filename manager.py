from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from info import create_app, db, models

# 调用方法，获取app
app = create_app("develop")

# 创建manager对象，管理app
manager = Manager(app)

# 使用Migrate关联app,db
Migrate(app, db)

# 给manager添加一条操作命令
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()
