from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from datetime import datetime as dt, timedelta
from dbms import generate_otp, login_required, admin_login_required
import smtplib
from os.path import isfile

app = Flask(__name__)

# Connecting to databases

# Companies database
company_profile_ = sqlite3.connect("database/companies.db", check_same_thread=False)
companies_db = company_profile_.cursor()
columns = ['Email', 'Company Name', 'Company Number', 'Company Address', 'password']
employee_columns = ['EmployeeID', 'FName', 'LName', 'email', 'DeptCode', 'Salary', 'JoinDate']
department_columns = ['Code', 'Name', 'ManagerID']
project_columns = ['ProjectID', 'Description', 'StartDate', 'DueDate', 'DeptCode']


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# SQLite functions
def add_to_table(table, dictionay, database):
    dictionay = dict(dictionay)
    key = tuple(dictionay.keys())
    value = tuple(dictionay.values())

    with database:
        database.cursor().execute("INSERT INTO" + f" '{table}' " + str(key) + " VALUES " + str(value))


def check_tables(id_, admin=True):

    if not admin:
        if not isfile('database/' + id_ + '.db'):
            return False

    global company, company_db


    company = sqlite3.connect('database/' + id_ + '.db', check_same_thread=False)
    company_db = company.cursor()

    if not len(company_db.execute('SELECT name from sqlite_master where type= "table"').fetchall()):
        with company:
            company_db.execute("""CREATE TABLE 'Employee' (
                'EmployeeID' integer PRIMARY KEY AUTOINCREMENT NOT NULL DEFAULT 100000, 
                'FName' varchar(200) NOT NULL,
                'LName' varchar(200),
                'Email' varchar(200) NOT NULL,
                'DeptCode' integer NOT NULL,
                'Salary' integer,
                'JoinDate' date NOT NULL,
                FOREIGN KEY('DeptCode') REFERENCES Department('Code')
                )""")
            company_db.execute("""CREATE TABLE 'Department'(
                'Code' integer PRIMARY KEY NOT NULL,
                'Name' varchar(100) NOT NULL,
                'ManagerID' integer NOT NULL,
                FOREIGN KEY('ManagerID') REFERENCES Employee('EmployeeID')
                )""")
            company_db.execute("""CREATE TABLE 'Project'(
                'ProjectID' integer PRIMARY KEY NOT NULL,
                'Description' text NOT NULL,
                'StartDate' date NOT NULL,
                'DueDate' date NOT NULL,
                'DeptCode' integer NOT NULL, 
                FOREIGN KEY('DeptCode') REFERENCES Department('Code')
            )""")
            company_db.execute("""CREATE TABLE 'WorksOn'(
                'EID' integer NOT NULL,
                'PID' integer NOT NULL,
                FOREIGN KEY('EID') REFERENCES Employee('EmployeeID'),
                FOREIGN KEY('PID') REFERENCES Project('ProjectID'),
                UNIQUE(EID, PID)
            )""")
    return True
            



@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():

    session.clear()

    if request.method == 'GET':
        return render_template('register.html')
    else:
        email = request.form.get('answer')
        generate_otp(email)
        session['email'] = email

        return redirect('/verify_otp')
    

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'GET':
        return render_template('verify_otp.html')
    else:
        return redirect('/Company_Profile')



@app.route('/Company_Profile', methods=['GET', 'POST'])
def company_profile():


    if not session:
        return redirect('/register')

    if request.method == 'GET':
        return render_template('Company_Profile.html')

    company_details = [None] * 5

    company_details[0] = session['email']
    company_details[1] = request.form.get('company-name')
    company_details[2] = request.form.get('company-number')
    company_details[3] = request.form.get('company-address')
    company_details[4] = request.form.get('password1')

    adding_dictionary = {columns[i] : company_details[i] for i in range(5)}

    session['user_id'] = session['email'].split('@')[0]

    check_tables(session.get('user_id'))

    add_to_table('Profiles', adding_dictionary, company_profile_)
    

    return redirect('/')
    

@app.route('/password', methods=['GET', 'POST'])
def pass_set():

    if request.method == 'GET':
        return render_template('password.html')

    pass1 = request.form.get('password')
    confirmation = request.form.get('confirmation')

    if pass1 != confirmation:
        return "ERROR!" #FOR_NOW
    
    session['password'] = pass1
    

    return redirect('/Company_Profile')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():

    session.clear()

    if request.method == 'GET':
        return render_template('admin_login.html', admin=True)


    email = request.form.get('email')
    password = request.form.get('password')

    with company_profile_:
        company = companies_db.execute("SELECT * FROM 'Profiles' WHERE email = :email",
                                {'email' : email}).fetchall()
    if len(company) != 1:
        return redirect('/admin_login')
    
    company = company[0]

    if company[4] != password:
        return "Password"
    
    session["user_id"] = email.split('@')[0]
    session["admin_login"] = True

    check_tables(session.get('user_id'))


    return redirect('/')

    
@app.route('/add_employee', methods=['GET', 'POST'])
@admin_login_required
def add_employee():
    
    if request.method == 'GET':
        return render_template('add_employee.html')
    else:

        employee_details = [None] * 7

        employee_details[0] = request.form.get('EmployeeID')
        employee_details[1] = request.form.get('fname')
        employee_details[2] = request.form.get('lname')
        employee_details[3] = request.form.get('email')
        employee_details[4] = request.form.get('DeptCode')
        employee_details[5] = request.form.get('Salary')
        employee_details[6] = request.form.get('JoinDate')

        adding_dictionary = {column : detail for column, detail in zip(employee_columns, employee_details)}

        add_to_table('Employee', adding_dictionary, company)


        return redirect('/add_employee') if int(request.form.get('method_')) else redirect('/')

    
@app.route('/add_department', methods=['GET', 'POST'])
@admin_login_required
def add_department():
    if request.method == 'GET':
        return render_template('add_department.html')
    else:
        add_to_table('Department', {column : request.form.get(column) for column in department_columns}, company)
        return redirect('/add_department')


@app.route('/add_project', methods=['GET', 'POST'])
@admin_login_required
def add_project():
    if request.method == 'GET':
        return render_template('add_project.html')
    else:
        add_to_table('Project', {column : request.form.get(column) for column in project_columns}, company)

        return redirect('/add_project')


@app.route('/search_employee')
def search_employee():
    answer = request.args.get('answer')
    info = company_db.execute('SELECT EmployeeID, FName, LName FROM Employee').fetchall()
    info = [inf for inf in info if str(inf[0]).startswith(answer)]
    
    return render_template('search.html', info=info)


@app.route('/assign_project', methods=['GET', 'POST'])
@admin_login_required
def assign_project():
    if request.method == 'GET':
        return render_template('assign_project.html')
    else:
        project_id = request.form.get('assigned_employees')
        employees_list = request.form.getlist('EmployeeID')
        previous_employees = company_db.execute("SELECT EID FROM WorksOn WHERE PID = :id", {'id' : project_id}).fetchall()
        previous_employees = set([str(emp[0]) for emp in previous_employees])
        for employee in previous_employees - set(employees_list):
            with company:
                company_db.execute("DELETE FROM WorksOn WHERE EID = :eid AND PID = :pid", {'eid' : employee, 'pid' : project_id})
        employees_list = set(employees_list) - previous_employees
        for employee in employees_list:
            adding_dictionary = {column : value for column, value in zip(['EID', 'PID'], [employee, project_id])}
            add_to_table('WorksOn', adding_dictionary, company)
        return redirect('/')



@app.route('/project_details')
@admin_login_required
def project_details():
    id_ = request.args.get('id')
    rows = company_db.execute("SELECT * FROM Project WHERE ProjectID = :id_", {'id_' : id_}).fetchall()
    if not len(rows):
        return jsonify(False)
    employees_list = company_db.execute("SELECT EID FROM WorksOn WHERE PID = :id_", {'id_' : id_}).fetchall()
    employees = []
    for employee in employees_list:
        values = company_db.execute("SELECT FName, LName FROM Employee WHERE EmployeeID = :id_", {'id_' : employee[0]}).fetchall()[0]
        employees.append((employee[0], values[0] + ' ' + values[1]))
    return jsonify([{column : value for column, value in zip(project_columns, rows[0])}, employees])
    

@app.route('/employee_login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'GET':
        return render_template('admin_login.html', admin=False)
    else:
        if not check_tables(request.form.get('company').split('@')[0], admin=False):
            return "Invalid Company" # For_Now
        else:
            rows = company_db.execute('SELECT * FROM Employee WHERE EmployeeID = :id AND Email = :email',
                                    {'id' : request.form.get('password'), 'email' : request.form.get('email')}).fetchall()
            if not len(rows):
                return "No Employee Found" # For_Now
            else: rows=rows[0]
            session['user_id'] = rows[0]
            session['admin_login'] = False
        return redirect('/')

@app.route('/view_projects')
@login_required
def view_projects():
    projects = list()
    employee = company_db.execute('SELECT FName, LName FROM Employee WHERE EmployeeID = :id', {'id' : session.get('user_id')}).fetchall()
    PIDs = company_db.execute('SELECT PID FROM WorksOn WHERE EID = :id', {'id' : session.get('user_id')})
    PIDs = [id_[0] for id_ in PIDs]
    for id_ in PIDs:
        project = list(company_db.execute('SELECT ProjectID, Description, StartDate, DueDate, DeptCode FROM Project WHERE ProjectID = :id', {'id' : id_}).fetchall()[0])
        project.append(True if dt.strptime(project[3], '%Y-%m-%d') > timedelta(days=7) + dt.now() else False)
        projects.append(project)
        
    
    return render_template('projects.html', employee=employee[0], projects=projects)

@app.route('/check_projectid')
def check_projectid():
    id_ = request.args.get('id')
    rows = company_db.execute(f'SELECT ProjectID FROM Project WHERE ProjectID = {id_}').fetchall()
    return jsonify(False) if not len(rows) else jsonify(True)
    




@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/')


@app.route('/hello_name')
def hello_name():
    name = request.args.get('name')
    return f'Hello {name}!' if name else 'Hello World'


@app.route('/new_page')
def new_page():
    return 'It\'s lonely in here.'


@app.route("/otp_verification", methods=["POST"])
def otp_verification():
    otp = request.form.get('otp')
    # FOR_NOW
    if (otp == session.get('my_var', None) or otp == '0000'):
        return jsonify(True)
    else:
        return jsonify(False)

if __name__ == "__main__":
    app.run(debug=True)
