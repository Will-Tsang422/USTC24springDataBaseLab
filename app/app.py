from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
# 自定义模块
import users
import query  # query.py中包含了所有的查询操作
import img
import CUD  # CUD.py中包含增删改操作
# logging模块用于调试
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='../templates',
            static_folder='../static')
app.config['SECRET_KEY'] = '2024spring-db-lab'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未登录时重定向到的页面

DEFAULT_IMG = 'static/images/default.png'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.errorhandler(404)  # 传入要处理的错误代码
def page_not_found(e):  # 接受异常对象作为参数
    return render_template('404.html'), 404  # 返回模板和状态码


@app.route('/employee_register', methods=['GET', 'POST'])
def employee_register():
    if request.method == 'POST':
        work_number = request.form.get('work_number')
        # 检查用户是否已经存在
        if users.check_employee_exists(work_number):
            message = '该工号已被注册'
            return render_template('employee_register.html', message=message)
        else:
            name = request.form.get('name')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            password = request.form.get('password')
            if users.insert_employee(work_number, password, name, age, gender, phone):
                flash('注册成功')
                return redirect(url_for('login'))
            else:
                message = '注册失败'
                return render_template('employee_register.html', message=message)
    else:
        message = '请填写注册信息'
        return render_template('employee_register.html', message=message)


@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        stu_number = request.form.get('stu_number')
        # 检查用户是否已经存在
        if users.check_student_exists(stu_number):
            message = '该学号已被注册'
        else:
            sname = request.form.get('name')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            degree = request.form.get('degree')
            password = request.form.get('password')
            if users.insert_student(stu_number, password, sname, age, gender, phone, degree):
                flash('注册成功')
                return redirect(url_for('login'))
            else:
                message = '注册失败'
                return render_template('student_register.html', message=message)
    else:
        message = '请填写注册信息'
        return render_template('student_register.html', message=message)


@login_manager.user_loader
def load_user(user_id):
    if user_id == 'admin':
        return users.Admin('admin')
    elif user_id[0] == 'E':
        employee_data = query.employee_info(user_id)
        if employee_data:
            return users.Employee(employee_data['eid'], employee_data['ename'], employee_data['age'], employee_data['gender'], employee_data['Tel'])
        return None
    elif user_id[0] == 'S':
        student_data = query.student_info(user_id)
        if student_data:
            return users.Student(student_data['sid'], student_data['sname'], student_data['age'], student_data['gender'], student_data['Tel'], student_data['degree'])
        return None


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form.get('userID')
        password = request.form.get('password')
        # 在这里添加您的登录逻辑
        if users.check_password(userID, password):
            if userID == 'admin':
                admin = users.Admin('admin')
                login_user(admin)
                return redirect(url_for('admin'))
            elif userID[0] == 'S':
                info = query.student_info(userID)
                student = users.Student(
                    info['sid'], info['sname'], info['age'], info['gender'], info['Tel'], info['degree'])
                login_user(student)
                return redirect(url_for('student'))
            elif userID[0] == 'E':
                info = query.employee_info(userID)
                employee = users.Employee(
                    info['eid'], info['ename'], info['age'], info['gender'], info['Tel'])
                login_user(employee)
                return redirect(url_for('employee'))
        else:
            flash('用户名或密码错误')
            return render_template('login.html')
    return render_template('login.html')

# 创建登出视图


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        userID = request.form['userID']
        old_password = request.form['oldPassword']
        new_password = request.form['newPassword']
        confirm_password = request.form['confirmPassword']
        if new_password != confirm_password:
            message = '两次密码不一致'
            return render_template('change_password.html', message=message)
        else:
            message = users.alter_password(userID, old_password, new_password)
            if message == 'success':
                flash('修改成功')
                return redirect(url_for('login'))
            else:
                return render_template('change_password.html', message=message)
    return render_template('change_password.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    canteens = query.canteens_info()
    canteens = query.merge_canteen_hours(canteens)
    windows = query.windows_info()
    pay_history = query.pay_history()
    employees = query.employees_info()
    month_earnings = query.month_earnings()
    names = [item['cname'] for item in month_earnings]
    totals = [item['total'] for item in month_earnings]
    print(names, totals)
    month_total = sum(totals)
    day_earnings = query.day_earnings()
    foods = query.all_food_info()
    supplys = query.supply_info()
    for food in foods:
        food['path'] = food.get('path') or DEFAULT_IMG
        food['on_sale'] = '是' if food['on_sale'] else '否'
    return render_template('admin.html', canteens=canteens, windows=windows, pay_history=pay_history, employees=employees, names=names, totals=totals, month_total=month_total, everyday=day_earnings, foods=foods, supplys=supplys)


@app.route('/update_window_number', methods=['POST'])
def update_window_number():
    eid = request.form.get('eid')
    new_window_number = request.form.get('newWindowNumber')
    CUD.update_window_number(eid, new_window_number)
    return redirect(url_for('admin'))


@app.route('/delete_employee', methods=['GET'])
def delete_employee():
    eid = request.args.get('eid')
    if eid:
        CUD.delete_employee(eid)
    return redirect(url_for('admin'))


@app.route('/delete_food', methods=['GET'])
def delete_food():
    fid = request.args.get('fid')
    if fid:
        CUD.delete_food(fid)
    return redirect(url_for('admin'))


@app.route('/insert_food', methods=['POST'])
def insert_food():
    fid = request.form.get('fid')
    fname = request.form.get('fname')
    price = request.form.get('price')
    wid = request.form.get('wid')
    meal_type = request.form.get('meal-type2')
    CUD.insert_food(fid, fname, price, wid, meal_type)
    return redirect(url_for('admin'))


@app.route('/delete_supply', methods=['POST'])
def delete_supply():
    fid = request.form.get('fid')
    wid = request.form.get('wid')
    meal_type = request.form.get('meal-type3')
    CUD.delete_supply(fid, wid, meal_type)
    return redirect(url_for('admin'))


@app.route('/update_canteen', methods=['POST'])
def update_canteen():
    canteen_id = request.form.get('canteen-id')
    canteen_name = request.form.get('canteen-name')
    meal_type = request.form.get('meal-type')
    open_time = request.form.get('open-time')
    close_time = request.form.get('close-time')
    if canteen_name == "删除":
        CUD.delete_canteen(canteen_id)
        print("fdasfdasfhadsklfhadsjkfhqewv fhoev")
    else:
        CUD.update_canteen(canteen_id, canteen_name, meal_type, open_time, close_time)
    return redirect(url_for('admin'))


@app.route('/update_window', methods=['POST'])
def update_window():
    wid = request.form.get('window-id')
    wname = request.form.get('window-name')
    cid = request.form.get('canteen-id2')
    CUD.update_window(wid, wname, cid)
    return redirect(url_for('admin'))


@app.route('/student', methods=['GET', 'POST'])
def student():
    canteens = query.canteens_info()
    canteens = query.merge_canteen_hours(canteens)
    windows = query.windows_info()
    userID = current_user.get_id()
    info = query.student_info(userID)
    pay_history = query.student_pay_history(userID)
    expense = query.student_expense(userID)['total']
    expense = expense if expense else 0
    foods = query.food_info()
    top_foods = query.today_top_foods()
    for food in foods:
        food['path'] = food.get('path') or DEFAULT_IMG
    for food in top_foods:
        food['path'] = food.get('path') or DEFAULT_IMG
    return render_template('student.html', canteens=canteens, student_info=info, pay_history=pay_history, total_expense=expense, foods=foods, top_foods=top_foods, windows=windows)


@app.route('/search_food', methods=['POST'])
def search_food():
    search_word = request.form.get('search')
    if search_word == 'all':
        return redirect(url_for('student'))
    canteens = query.canteens_info()
    canteens = query.merge_canteen_hours(canteens)
    windows = query.windows_info()
    userID = current_user.get_id()
    info = query.student_info(userID)
    pay_history = query.student_pay_history(userID)
    expense = query.student_expense(userID)['total']
    expense = expense if expense else 0
    foods = query.food_info(search_word)
    top_foods = query.today_top_foods()
    for food in foods:
        food['path'] = food.get('path') or DEFAULT_IMG
    for food in top_foods:
        food['path'] = food.get('path') or DEFAULT_IMG
    return render_template('student.html', canteens=canteens, student_info=info, pay_history=pay_history, total_expense=expense, foods=foods, top_foods=top_foods, windows=windows)


@app.route('/buy_food', methods=['POST'])
def buy_food():
    fid = request.form.get('fid')
    quantity = request.form.get('quantity')
    wid = request.form.get('wid')
    userID = current_user.get_id()
    result = CUD.buy_food(userID, fid, quantity, wid)
    result = result['@state']
    print(result)
    if result == 1:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'fail'}), 400


@app.route('/recharge', methods=['POST'])
def recharge():
    userID = current_user.get_id()
    amount = request.form.get('recharge')
    CUD.recharge(userID, amount)
    return redirect(url_for('student'))


@app.route('/employee', methods=['GET', 'POST'])
def employee():
    canteens = query.canteens_info()
    canteens = query.merge_canteen_hours(canteens)
    windows = query.windows_info()
    userID = current_user.get_id()
    info = query.employee_info(userID)
    dishes = query.window_info(userID)
    breakfast = [dish for dish in dishes if dish['meal_type'] == '早餐']
    lunch = [dish for dish in dishes if dish['meal_type'] == '午餐']
    dinner = [dish for dish in dishes if dish['meal_type'] == '晚餐']
    sale = query.today_sale(userID)['total']
    sale = sale if sale else 0
    return render_template('employee.html', canteens=canteens, employee_info=info, breakfast=breakfast, lunch=lunch, dinner=dinner, total_income=sale, windows=windows)


@app.route('/update_phone', methods=['GET', 'POST'])
def update_phone():
    if request.method == 'POST':
        userID = current_user.get_id()
        phone = request.form.get('phone')
        if userID[0] == 'S':
            CUD.update_student_phone(userID, phone)
            return redirect(url_for('student'))
        elif userID[0] == 'E':
            CUD.update_employee_phone(userID, phone)
            return redirect(url_for('employee'))


@app.route('/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    form = img.UploadForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        file = form.file.data
        if file and img.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # 保存图片路径到数据库
            CUD.upload_avatar(user_id, file_path)
            return redirect(url_for('admin'))

    return render_template('upload_avatar.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
