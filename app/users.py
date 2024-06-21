import pymysql
from config import DB_CONFIG
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
# logging模块用于调试
import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

def check_employee_exists(userid):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 执行SQL语句
    sql = 'SELECT * FROM Employee WHERE eid=%s'
    cursor.execute(sql, (userid,))
    # 获取查询结果
    result = cursor.fetchone()
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    # 判断用户是否存在
    return result is not None

def check_student_exists(userid):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 执行SQL语句
    sql = 'SELECT * FROM Student WHERE sid=%s'
    cursor.execute(sql, (userid,))
    # 获取查询结果
    result = cursor.fetchone()
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    # 判断用户是否存在
    return result is not None

def check_password(userID, password):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    with db.cursor() as cursor:
        # 执行SQL语句
        sql = 'SELECT * FROM identification WHERE id=%s'
        cursor.execute(sql, (userID,))
        # 获取查询结果
        result = cursor.fetchone()
    db.close()
    # 比较密码
    if result is not None:
        return check_password_hash(result['password'], password)
    else:
        return False

def insert_employee(userid, password, name, age, gender, phone):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    # 执行SQL语句
    with db.cursor() as cursor:
        try:
            password = generate_password_hash(password)
            sql = 'INSERT INTO identification(id, password) VALUES (%s, %s)'
            cursor.execute(sql, (userid, password))
            sql = 'INSERT INTO Employee(eid, ename, age, gender, Tel) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (userid, name, age, gender, phone))
            db.commit()
            db.close()
            return True
        except Exception as e:
            print(e)
            db.rollback()
            db.close()
            return False

def insert_student(userid, password, name, age, gender, phone, degree):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    # 执行SQL语句
    with db.cursor() as cursor:
        try:
            password = generate_password_hash(password)
            sql = 'INSERT INTO identification(id, password) VALUES (%s, %s)'
            cursor.execute(sql, (userid, password))
            sql = 'INSERT INTO Student(sid, sname, age, gender, Tel, degree) VALUES (%s, %s, %s, %s, %s, %s)'
            cursor.execute(sql, (userid, name, age, gender, phone, degree))
            db.commit()
            db.close()
            return True
        except Exception as e:
            logging.error(e)
            db.rollback()
            db.close()
            return False

def alter_password(userid, old_password, new_password):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    # 执行SQL语句
    with db.cursor() as cursor:
        try:
            sql = 'SELECT password FROM identification WHERE id=%s'
            cursor.execute(sql, (userid,))
            result = cursor.fetchone()
            if check_password_hash(result['password'], old_password):
                new_password = generate_password_hash(new_password)
                sql = 'UPDATE identification SET password=%s WHERE id=%s'
                cursor.execute(sql, (new_password, userid))
                db.commit()
                db.close()
                return 'success'
            else:
                db.close()
                return '原密码错误！'
        except Exception as e:
            logging.error(e)
            db.close()
            return e


class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

class Student(UserMixin):
    def __init__(self, sid, sname, age, gender, Tel, degree):
        self.id = sid
        self.sid = sid
        self.sname = sname
        self.age = age
        self.gender = gender
        self.Tel = Tel
        self.degree = degree
    
    def get_id(self):
        return self.sid

class Employee(UserMixin):
    def __init__(self, eid, ename, age, gender, Tel):
        self.id = eid
        self.eid = eid
        self.ename = ename
        self.age = age
        self.gender = gender
        self.Tel = Tel
    
    def get_id(self):
        return self.eid



