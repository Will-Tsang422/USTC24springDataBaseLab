import pymysql
from datetime import datetime, timedelta
from config import DB_CONFIG
# logging模块用于调试
import logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


def exec_sql(sql, params=None):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    with db.cursor() as cursor:
        try:
            # 执行SQL语句
            cursor.execute(sql, params)
            # 如果正常执行，提交事务
            db.commit()
            db.close()
            return True
        except Exception as e:
            logging.error(e)
            # 如果执行出错，回滚事务
            db.rollback()
            db.close()
            return False

def update_student_phone(userID, new_phone):
    sql = "UPDATE Student SET Tel=%s WHERE sid=%s"
    return exec_sql(sql, (new_phone, userID))

def update_employee_phone(userID, new_phone):
    sql = "UPDATE Employee SET Tel=%s WHERE eid=%s"
    return exec_sql(sql, (new_phone, userID))

def update_window_number(eid, wid):
    if wid == '0':
        wid = None
    sql = "UPDATE Employee SET wid=%s WHERE eid=%s"
    return exec_sql(sql, (wid, eid))

def delete_employee(eid):
    sql = "DELETE FROM Employee WHERE eid=%s"
    return exec_sql(sql, (eid,))

def delete_food(fid):
    sql = 'CALL delete_food(%s)'
    return exec_sql(sql, (fid,))

def insert_food(fid, fname, price, wid, meal_type):
    sql = 'CALL insert_food(%s, %s, %s, %s, %s)'
    return exec_sql(sql, (fid, fname, price, wid, meal_type))

def delete_supply(fid, wid, meal_type):
    sql = 'DELETE FROM SUPPLY WHERE fid=%s AND wid=%s AND meal_type=%s'
    return exec_sql(sql, (fid, wid, meal_type))

def update_canteen(canteen_id, canteen_name, meal_type, open_time, close_time):
    open_time = datetime.strptime(open_time, '%H:%M:%S')
    close_time = datetime.strptime(close_time, '%H:%M:%S')
    sql = 'CALL insert_canteen(%s, %s, %s, %s, %s)'
    return exec_sql(sql, (canteen_id, canteen_name, meal_type, open_time, close_time))

def delete_canteen(canteen_id):
    sql = 'CALL delete_canteen(%s)'
    return exec_sql(sql, (canteen_id,))

def update_window(wid, wname, cid):
    sql = 'CALL insert_window(%s, %s, %s)'
    return exec_sql(sql, (wid, wname, cid))

def recharge(userID, amount):
    sql = "UPDATE Student SET money=money+%s WHERE sid=%s"
    return exec_sql(sql, (amount, userID))

def upload_avatar(fid, file):
    sql = 'UPDATE Food SET path=%s WHERE fid=%s'
    return exec_sql(sql, (file, fid))

def buy_food(sid, fid, count, wid):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = 'CALL buy_food(%s, %s, %s, %s, @state)'
        cursor.execute(sql, (sid, fid, count, wid))
        sql = 'SELECT @state'
        cursor.execute(sql)
        result = cursor.fetchone()
        connection.commit()
    connection.close()
    return result