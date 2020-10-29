from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from dbms import generate_otp, login_required
import smtplib

app = Flask(__name__)

# Connecting to databases

# Companies database
company_profile_ = sqlite3.connect("database/companies.db", check_same_thread=False)
companies_db = company_profile_.cursor()
columns = ['Email', 'Company Name', 'Company Number', 'Company Address', 'password']
employee_columns = ['EmployeeID', 'FName', 'LName', 'email', 'DeptCode', 'Salary', 'JoinDate']



# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# SQLite functions
def add_to_table(table, dictionay, database, cursor):
    dictionay = dict(dictionay)
    key = tuple(dictionay.keys())
    value = tuple(dictionay.values())

    with database:
        cursor.execute("INSERT INTO" + f" '{table}' " + str(key) + " VALUES " + str(value))


def check_tables():
    id_ = session.get('user_id')

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
                FOREIGN KEY('PID') REFERENCES Project('ProjectID')
            )""")
            



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

    check_tables()

    add_to_table('Profiles', adding_dictionary, company_profile_, companies_db)
    

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
        return render_template('admin_login.html')


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

    check_tables()


    return redirect('/')

    
@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
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

        add_to_table('Employee', adding_dictionary, company, company_db)


        return redirect('/add_employee') if int(request.form.get('method_')) else redirect('/')

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
