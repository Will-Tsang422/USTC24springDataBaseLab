import pymysql
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from config import DB_CONFIG

def exec_sql(sql, params=None, fetchall=True):
    # 连接数据库
    db = pymysql.connect(**DB_CONFIG)
    with db.cursor() as cursor:
        # 执行SQL语句
        cursor.execute(sql, params)
        # 获取查询结果
        if fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
    db.close()
    return result

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

def canteens_info():
    sql = '''
    SELECT cname, meal_type, open_time, close_time FROM Canteen
    JOIN CanteenHours ON Canteen.cid = CanteenHours.cid
    '''
    return exec_sql(sql)

def all_food_info():
    sql = '''
    SELECT * FROM Food
    ORDER BY fid
    '''
    return exec_sql(sql)

def windows_info():
    sql = '''
    SELECT wid, wname, Canteen.cid, cname FROM `Window` JOIN Canteen ON `Window`.cid = Canteen.cid
    '''
    return exec_sql(sql)

def food_info(word=None):
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
    return exec_sql(sql)

def supply_info():
    sql = '''
    SELECT Food.fid, fname, wid, meal_type FROM
    Supply JOIN Food ON Food.fid = SUPPLY.fid
    ORDER BY fid
    '''
    return exec_sql(sql)

def today_top_foods():
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
    return exec_sql(sql, (date, next_date))

def pay_history():
    sql = '''
    SELECT deal_time, sid, Income.wid, (quantity*price) AS earnings FROM 
    Income JOIN Food ON Income.fid = Food.fid
    JOIN `Window` ON Income.wid = `Window`.wid
    ORDER BY deal_time DESC
    '''
    return exec_sql(sql)

def student_info(userID):
    sql = '''
    SELECT sid, sname, age, gender, Tel, degree, money FROM Student WHERE sid=%s
    '''
    return exec_sql(sql, (userID,), fetchall=False)

def employee_info(userID):
    sql = '''
    SELECT eid, ename, age, gender, Tel, Employee.wid, wname FROM 
    Employee LEFT JOIN `Window` ON Employee.wid = `Window`.wid
    WHERE eid=%s
    '''
    return exec_sql(sql, (userID,), fetchall=False)

def employees_info():
    sql = '''
    SELECT eid, ename, age, gender, Tel, wid FROM Employee ORDER BY eid
    '''
    return exec_sql(sql)

def window_info(userID):
    # 窗口菜品信息
    sql = '''
    SELECT fname, price, meal_type FROM
    (SELECT fid, meal_type FROM SUPPLY 
    WHERE wid = (SELECT wid FROM Employee WHERE eid=%s)) AS win_sup
    JOIN Food ON win_sup.fid = Food.fid
    WHERE on_sale = 1
    '''
    return exec_sql(sql, (userID,))

def today_sale(userID):
    date = datetime.now().strftime('%Y-%m-%d')
    next_date = datetime.now() + timedelta(days=1)
    sql = '''
    SELECT SUM(quantity*price) AS total FROM Income JOIN Food ON Income.fid = Food.fid
    WHERE wid = (SELECT wid FROM Employee WHERE eid=%s) AND deal_time >= %s AND deal_time < %s
    '''
    return exec_sql(sql, (userID, date, next_date), fetchall=False)

def student_pay_history(userID):
    sql = '''
    SELECT deal_time, fname, quantity, price, wid FROM
    (SELECT wid, fid, quantity, deal_time, sid FROM Income WHERE sid=%s) AS pay_history
    JOIN Food ON pay_history.fid = Food.fid
    ORDER BY deal_time DESC
    '''
    return exec_sql(sql, (userID,))

def student_expense(userID):
    sql = '''
    SELECT SUM(quantity*price) AS total FROM 
    Income JOIN Food ON Income.fid = Food.fid
    WHERE sid=%s
    '''
    return exec_sql(sql, (userID,), fetchall=False)

# 统计当月每个食堂的总收入
def month_earnings():
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
    return exec_sql(sql, (month, next_month))

#  统计每天的总收入, 包括一天的早中晚餐
def day_earnings():
    sql = '''
    SELECT DATE(deal_time) as date, SUM(quantity*price) AS total FROM Income
    JOIN Food ON Income.fid = Food.fid
    GROUP BY date
    ORDER BY date DESC
    '''
    return exec_sql(sql)