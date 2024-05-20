from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pymysql
import logging
from config import DB_CONFIG
# 自定义模块
from users import *
from query import *
from img import *
from refresh import *

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = '2024spring-db-lab'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB

# 初始化Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # 未登录时重定向到的页面

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')

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
        if check_employee_exists(work_number):
            message = '该工号已被注册'
            return render_template('employee_register.html', message=message)
        else:
            name = request.form.get('name')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            password = request.form.get('password')
            if insert_employee(work_number, password, name, age, gender, phone):
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
        if check_student_exists(stu_number):
            message = '该学号已被注册'
        else:
            sname = request.form.get('name')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            phone = request.form.get('phone')
            degree = request.form.get('degree')
            password = request.form.get('password')
            if insert_student(stu_number, password, sname, age, gender, phone, degree):
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
        return Admin('admin')
    elif user_id[0] == 'E':
        employee_data = employee_info(user_id)
        if employee_data:
            return Employee(employee_data['eid'], employee_data['ename'], employee_data['age'], employee_data['gender'], employee_data['Tel'])
        return None
    elif user_id[0] == 'S':
        student_data = student_info(user_id)
        if student_data:
            return Student(student_data['sid'], student_data['sname'], student_data['age'], student_data['gender'], student_data['Tel'], student_data['degree'])
        return None



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userID = request.form.get('userID')
        password = request.form.get('password')
        # 在这里添加您的登录逻辑
        if check_password(userID, password):
            if userID == 'admin':
                admin = Admin('admin')
                login_user(admin)
                return redirect(url_for('admin'))
            elif userID[0] == 'S':
                info = student_info(userID)
                student = Student(info['sid'], info['sname'], info['age'], info['gender'], info['Tel'], info['degree'])
                login_user(student)
                return redirect(url_for('student'))
            elif userID[0] == 'E':
                info = employee_info(userID)
                logging.debug(info)
                employee = Employee(info['eid'], info['ename'], info['age'], info['gender'], info['Tel'])
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
            message = alter_password(userID, old_password, new_password)
            if message == 'success':
                flash('修改成功')
                return redirect(url_for('login'))
            else:
                return render_template('change_password.html', message=message)
    return render_template('change_password.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    canteens = canteen_info()
    canteens = merge_canteen_hours(canteens)
    windows = windows_info()
    pay_history = payment_history()
    employees_info = employees()
    earnings = month_earnings()
    names = [item['cname'] for item in earnings]
    totals = [item['total'] for item in earnings]
    today_total = sum(totals)
    everyday = everyday_earnings()
    foods = all_food_info()
    supplys = supply_info()
    for food in foods:
        if food['path'] == None:
            food['path'] = 'static/images/default.png'
    return render_template('admin.html', canteens=canteens, windows=windows, pay_history=pay_history, employees=employees_info, names=names, totals=totals, today_total=today_total, everyday=everyday, foods=foods, supplys=supplys)

@app.route('/update_window_number', methods=['POST'])
def update_window_number():
    eid = request.form.get('eid')
    new_window_number = request.form.get('newWindowNumber')
    logging.debug(eid)
    logging.debug(new_window_number)
    update_employee_window(eid, new_window_number)
    return redirect(url_for('admin'))

@app.route('/delete_employee', methods=['GET'])
def delete_employee():
    eid = request.args.get('eid')
    if eid:
        delete_empl(eid)
    return redirect(url_for('admin'))

@app.route('/delete_food', methods=['GET'])
def delete_food():
    fid = request.args.get('fid')
    if fid:
        delete_f(fid)
    return redirect(url_for('admin'))

@app.route('/insert_food', methods=['POST'])
def insert_food():
    fid = request.form.get('fid')
    fname = request.form.get('fname')
    price = request.form.get('price')
    wid = request.form.get('wid')
    meal_type = request.form.get('meal-type2')
    insert_f(fid, fname, price, wid, meal_type)
    return redirect(url_for('admin'))

@app.route('/delete_supply', methods=['POST'])
def delete_supply():
    fid = request.form.get('fid')
    wid = request.form.get('wid')
    meal_type = request.form.get('meal-type3')
    delete_supply_info(fid, wid, meal_type)
    return redirect(url_for('admin'))

@app.route('/update_canteen', methods=['POST'])
def update_canteen():
    canteen_id = request.form.get('canteen-id')
    canteen_name = request.form.get('canteen-name')
    meal_type = request.form.get('meal-type')
    open_time = request.form.get('open-time')
    close_time = request.form.get('close-time')
    update_canteen_info(canteen_id, canteen_name, meal_type, open_time, close_time)
    return redirect(url_for('admin'))

@app.route('/update_window', methods=['POST'])
def update_window():
    wid = request.form.get('window-id')
    wname = request.form.get('window-name')
    cid = request.form.get('canteen-id2')
    update_window_info(wid, wname, cid)
    return redirect(url_for('admin'))

@app.route('/student', methods=['GET', 'POST'])
def student():
    canteens = canteen_info()
    canteens = merge_canteen_hours(canteens)
    windows = windows_info()
    userID = current_user.get_id()
    info = student_info(userID)
    pay_history, total = student_pay_history(userID)
    foods = food_info()
    top_foods = today_top_food()
    if total == None:
        total = 0
    for food in foods:
        if food['path'] == None:
            food['path'] = 'static/images/default.png'
    for food in top_foods:
        if food['path'] == None:
            food['path'] = 'static/images/default.png'
    return render_template('student.html', canteens=canteens, student_info=info, pay_history=pay_history, total_expense=total, foods=foods, top_foods=top_foods, windows=windows)

@app.route('/search_food', methods=['GET', 'POST'])
def search_food():
    if request.method == 'POST':
        search_word = request.form.get('search')
        if search_word == 'all':
            return redirect(url_for('student'))
        canteens = canteen_info()
        canteens = merge_canteen_hours(canteens)
        windows = windows_info()
        userID = current_user.get_id()
        info = student_info(userID)
        pay_history, total = student_pay_history(userID)
        foods = food_info(search_word)
        top_foods = today_top_food()
        if total == None:
            total = 0
        for food in foods:
            if food['path'] == None:
                food['path'] = 'static/images/default.png'
        for food in top_foods:
            if food['path'] == None:
                food['path'] = 'static/images/default.png'
        return render_template('student.html', canteens=canteens, student_info=info, pay_history=pay_history, total_expense=total, foods=foods, top_foods=top_foods, windows=windows)
    else:
        return redirect(url_for('student'))


@app.route('/buy_food', methods=['POST'])
def buy_food():
    fid = request.form.get('fid')
    quantity = request.form.get('quantity')
    wid = request.form.get('wid')
    userID = current_user.get_id()
    result = purchase_food(userID, fid, quantity, wid)
    result = result['@state']
    logging.debug(result)
    if result == 1:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'fail'}), 400

@app.route('/recharge', methods=['POST'])
def recharge():
    userID = current_user.get_id()
    amount = request.form.get('recharge')
    student_recharge(userID, amount)
    return redirect(url_for('student'))

@app.route('/employee', methods=['GET', 'POST'])
def employee():
    canteens = canteen_info()
    canteens = merge_canteen_hours(canteens)
    windows = windows_info()
    userID = current_user.get_id()
    info = employee_info(userID)
    dishes, total = window_info(userID)
    if total == None:
        total = 0
    return render_template('employee.html', canteens=canteens, employee_info=info, dishes=dishes, total_income=total, windows=windows)

@app.route('/update_phone', methods=['GET', 'POST'])
def update_phone():
    if request.method == 'POST':
        userID = current_user.get_id()
        phone = request.form.get('phone')
        if userID[0] == 'S':
            update_student_phone(userID, phone)
            return redirect(url_for('student'))
        elif userID[0] == 'E':
            update_employee_phone(userID, phone)
            return redirect(url_for('employee'))

@app.route('/upload_avatar', methods=['GET', 'POST'])
@login_required
def upload_avatar():
    form = UploadForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        file = form.file.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            # 保存图片路径到数据库
            upload_img(user_id, file_path)
            return redirect(url_for('admin'))
    
    return render_template('upload_avatar.html', form=form)




if __name__ == '__main__':
    app.run(debug=True)
