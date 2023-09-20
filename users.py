from db import db
from flask import session
from sqlalchemy.sql import text
from werkzeug.security import check_password_hash, generate_password_hash

def get_user(id):
    sql = text("SELECT * FROM users WHERE user_id=:id")
    result = db.session.execute(sql, {"id":id})
    return result.fetchone()

def get_users():
    sql = text("SELECT user_id, user_username FROM users ORDER BY user_username")
    result = db.session.execute(sql)
    return result.fetchall()


def login(username, password):
    sql = text("SELECT user_id, user_password, user_isadmin FROM users WHERE user_username=:username")
    result = db.session.execute(sql, {"username":username})
    user = result.fetchone()
    if not user:
        return False
    if not check_password_hash(user[1], password):
        return False
    session["id"] = user[0]
    session["username"] = username
    session["is_admin"] = user[2]
    return True

def signup(username, password, is_admin):
    hash_value = generate_password_hash(password)
    try:
        sql = text("""INSERT INTO users (user_username, user_password, user_isadmin)
                 VALUES (:username, :password, :is_admin)""")
        db.session.execute(sql, {"username":username, "password":hash_value, "is_admin":is_admin})
        db.session.commit()
    except:
        return False
    return login(username, password)