import pymysql
from datetime import datetime, timedelta
from config import DB_CONFIG

def update_student_phone(userID, new_phone):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = "UPDATE Student SET Tel=%s WHERE sid=%s"
        cursor.execute(sql, (new_phone, userID))
        connection.commit()
    connection.close()

def update_employee_phone(userID, new_phone):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = "UPDATE Employee SET Tel=%s WHERE eid=%s"
        cursor.execute(sql, (new_phone, userID))
        connection.commit()
    connection.close()

def update_employee_window(eid, wid):
    connection = pymysql.connect(**DB_CONFIG)
    if wid == '0':
        wid = None
    with connection.cursor() as cursor:
        sql = "UPDATE Employee SET wid=%s WHERE eid=%s"
        cursor.execute(sql, (wid, eid))
        connection.commit()
    connection.close()

def delete_empl(eid):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = "DELETE FROM Employee WHERE eid=%s"
        cursor.execute(sql, (eid,))
        connection.commit()
    connection.close()

def delete_f(fid):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = 'CALL delete_food(%s)'
        cursor.execute(sql, (fid,))
        connection.commit()
    connection.close()

def insert_f(fid, fname, price, wid, meal_type):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = 'CALL insert_food(%s, %s, %s, %s, %s)'
        cursor.execute(sql, (fid, fname, price, wid, meal_type))
        connection.commit()
    connection.close()

def delete_supply_info(fid, wid, meal_type):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = 'DELETE FROM SUPPLY WHERE fid=%s AND wid=%s AND meal_type=%s'
        cursor.execute(sql, (fid, wid, meal_type))
        connection.commit()
    connection.close()

def update_canteen_info(canteen_id, canteen_name, meal_type, open_time, close_time):
    connection = pymysql.connect(**DB_CONFIG)
    open_time = datetime.strptime(open_time, '%H:%M:%S')
    close_time = datetime.strptime(close_time, '%H:%M:%S')
    with connection.cursor() as cursor:
        sql = 'CALL insert_canteen(%s, %s, %s, %s, %s)'
        cursor.execute(sql, (canteen_id, canteen_name, meal_type, open_time, close_time))
        connection.commit()
    connection.close()

def update_window_info(wid, wname, cid):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        try:
            sql = 'CALL insert_window(%s, %s, %s)'
            cursor.execute(sql, (wid, wname, cid))
            connection.commit()
        except Exception as e:
            print(e)
    connection.close()

def student_recharge(userID, amount):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = "UPDATE Student SET money=money+%s WHERE sid=%s"
        cursor.execute(sql, (amount, userID))
        connection.commit()
    connection.close()

def upload_img(fid, file):
    connection = pymysql.connect(**DB_CONFIG)
    with connection.cursor() as cursor:
        sql = 'UPDATE Food SET path=%s WHERE fid=%s'
        cursor.execute(sql, (file, fid))
        connection.commit()
    connection.close()

def purchase_food(sid, fid, count, wid):
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