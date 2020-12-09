from flask import session, current_app, g
from functools import wraps


def check_login(view_func):
    @wraps(view_func)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id")
        user = None
        if user_id:
            try:
                from news.models import User
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        #3.将user数据封装到g对象
        g.user = user
        return view_func(*args,**kwargs)
    return wrapper