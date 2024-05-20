import pymysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import DB_CONFIG


def merge_canteen_hours(canteens):
    merged_canteens = {}
    for canteen in canteens:
        cname = canteen['cname']
        meal_type = canteen['meal_type']
        open_time = canteen['open_time']
        close_time = canteen['close_time']
        if cname not in merged_canteens:
            merged_canteens[cname] = {'cname': cname}
        merged_canteens[cname][meal_type] = f"{open_time} - {close_time}"
    return list(merged_canteens.values())

def canteen_info():
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 执行SQL语句
    sql = '''
    SELECT cname, meal_type, open_time, close_time FROM Canteen
    JOIN CanteenHours ON Canteen.cid = CanteenHours.cid
    '''
    cursor.execute(sql)
    # 获取查询结果
    result = cursor.fetchall()
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    return result

def all_food_info():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT Food.fid, path, fname, price, wname, cname FROM
    Food LEFT JOIN SUPPLY ON Food.fid = SUPPLY.fid
    LEFT JOIN `Window` ON SUPPLY.wid = `Window`.wid
    LEFT JOIN Canteen ON `Window`.cid = Canteen.cid
    WHERE on_sale = 1
    ORDER BY fid
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def windows_info():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT wid, wname, Canteen.cid, cname FROM `Window` JOIN Canteen ON `Window`.cid = Canteen.cid
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def food_info(word=None):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    if word:
        sql = f'''
        SELECT Food.fid, path, fname, price, wname, SUPPLY.wid, cname, meal_type FROM
        Food JOIN SUPPLY ON Food.fid = SUPPLY.fid
        JOIN `Window` ON SUPPLY.wid = `Window`.wid
        JOIN Canteen ON `Window`.cid = Canteen.cid
        WHERE on_sale = 1 AND fname LIKE '%{word}%'
        ORDER BY fid
        '''
    else:
        sql = '''
        SELECT Food.fid, path, fname, price, wname, SUPPLY.wid, cname, meal_type FROM
        Food JOIN SUPPLY ON Food.fid = SUPPLY.fid
        JOIN `Window` ON SUPPLY.wid = `Window`.wid
        JOIN Canteen ON `Window`.cid = Canteen.cid
        WHERE on_sale = 1
        ORDER BY fid
        '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def supply_info():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT Food.fid, fname, wid, meal_type FROM
    Supply JOIN Food ON Food.fid = SUPPLY.fid
    ORDER BY fid
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def today_top_food():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 得到电脑时间
    date = datetime.now().strftime('%Y-%m-%d')
    next_date = datetime.now() + timedelta(days=1)
    sql = '''
    SELECT top_food.fid, fname, path, total FROM
    (SELECT Income.fid, SUM(quantity) AS total FROM Income
    JOIN Food ON Income.fid = Food.fid
    WHERE deal_time >= %s AND deal_time < %s
    GROUP BY fid
    ORDER BY total DESC
    LIMIT 3) AS top_food
    JOIN Food ON top_food.fid = Food.fid
    '''
    cursor.execute(sql, (date, next_date))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def payment_history():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT deal_time, sid, Income.wid, (quantity*price) AS earnings FROM 
    Income JOIN Food ON Income.fid = Food.fid
    JOIN `Window` ON Income.wid = `Window`.wid
    ORDER BY deal_time DESC
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def student_info(userID):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 执行SQL语句，取出
    sql = 'SELECT sid, sname, age, gender, Tel, degree, money FROM Student WHERE sid=%s'
    cursor.execute(sql, (userID,))
    # 获取查询结果
    result = cursor.fetchone()
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    return result

def employee_info(userID):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 执行SQL语句
    sql = '''SELECT eid, ename, age, gender, Tel, Employee.wid, wname FROM 
    Employee LEFT JOIN `Window` ON Employee.wid = `Window`.wid
    WHERE eid=%s
    '''
    cursor.execute(sql, (userID,))
    # 获取查询结果
    result = cursor.fetchone()
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    return result

def employees():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = 'SELECT eid, ename, age, gender, Tel, wid FROM Employee ORDER BY eid'
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

def window_info(userID):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    # 窗口菜品信息
    sql = '''
    SELECT fname, price FROM Food WHERE fid IN
    (SELECT fid FROM SUPPLY 
    WHERE wid= (SELECT wid FROM Employee WHERE eid=%s)) AND on_sale=1
    '''
    cursor.execute(sql, (userID,))
    dishes = cursor.fetchall()
    # 今日销售额
    date = datetime.now().strftime('%Y-%m-%d')
    print(date)
    next_date = datetime.now() + timedelta(days=1)
    sql = '''
    SELECT SUM(quantity*price) AS total FROM Income JOIN Food ON Income.fid = Food.fid
    WHERE wid = (SELECT wid FROM Employee WHERE eid=%s) AND deal_time >= %s AND deal_time < %s
    '''
    cursor.execute(sql, (userID, date, next_date))
    total = cursor.fetchone()['total']
    cursor.close()
    db.close()
    return dishes, total

def student_pay_history(userID):
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT deal_time, fname, quantity, price, wid FROM
    (SELECT wid, fid, quantity, deal_time, sid FROM Income WHERE sid=%s) AS pay_history
    JOIN Food ON pay_history.fid = Food.fid
    ORDER BY deal_time DESC
    '''
    cursor.execute(sql, (userID,))
    result = cursor.fetchall()
    
    # 计算消费总额
    sql = '''
    SELECT SUM(quantity*price) AS total FROM 
    Income JOIN Food ON Income.fid = Food.fid
    WHERE sid=%s
    '''
    cursor.execute(sql, (userID,))
    total = cursor.fetchone()['total']
    
    cursor.close()
    db.close()
    return result, total


# 统计当月每个食堂的总收入
def month_earnings():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
    next_month = (datetime.now() + relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d')
    sql = '''
    SELECT cname, SUM(quantity*price) AS total FROM 
    Income JOIN Food ON Income.fid = Food.fid
    JOIN `Window` ON Income.wid = `Window`.wid
    JOIN Canteen ON `Window`.cid = Canteen.cid
    WHERE deal_time >= %s AND deal_time < %s
    GROUP BY cname
    '''
    cursor.execute(sql, (month, next_month))
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result

#  统计每天的总收入, 包括一天的早中晚餐
def everyday_earnings():
    db = pymysql.connect(**DB_CONFIG)
    cursor = db.cursor()
    sql = '''
    SELECT DATE(deal_time) as date, SUM(quantity*price) AS total FROM Income
    JOIN Food ON Income.fid = Food.fid
    GROUP BY date
    ORDER BY date DESC
    '''
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result