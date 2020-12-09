from news import create_app, db, models # 导入models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from news.models import User
from flask import session, current_app
from datetime import datetime,timedelta
from random import randint

#工厂方法，获取APP
app = create_app("dev")

manager = Manager(app)
Migrate(app, db)
manager.add_command("db", MigrateCommand)


# 定义方法：创建管理员对象
# @manager.option() 给manager添加一个脚本运行的方法
# 在终端运行命令： python index.py create_superuser -u admin -p 123456
@manager.option('-u', '--username', dest="username")
@manager.option('-p', '--password', dest='password')
def create_superuser(username, password):
    admin = User()
    admin.nick_name = username
    admin.mobile = username
    admin.password = password
    admin.is_admin = True

    try:
        db.session.add(admin)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "创建管理员用户失败！"
    return "创建管理员账号成功！"

#添加测试用户
@manager.option('-t', '--test', dest='test')
def add_test_user(test):

    #1.定义容器
    user_list = []

    #2.for循环创建1000个用户
    for i in range(0,100):
        user = User()
        user.nick_name = "老王%s"%i
        user.mobile = "138%08d"%i
        user.password_hash = "pbkdf2:sha256:50000$aKqdryiI$c7a6e0e7f550cf8710def5eafda02fd36547d938bad71b8a40466830764aec6e"
        #设置用户的登陆时间为近31天的
        user.last_login = datetime.now() - timedelta(seconds=randint(0,3600*24*31))

        user_list.append(user)

    #3.将用户添加到数据库中
    try:
        db.session.add_all(user_list)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return "添加测试用户失败"

    return "添加测试用户成功"


if __name__ == "__main__":
    manager.run()

#迁移命令
# python index.py db init
# python index.py db migrate -m "init"
# python index.py db upgrade
