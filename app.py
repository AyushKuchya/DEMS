from flask import Flask, render_template, request, redirect, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from dbms import generate_otp
import smtplib

app = Flask(__name__)

# Connecting to database
conn = sqlite3.connect("companies.db", check_same_thread=False)
db = conn.cursor()
columns = ['Email', 'Company Name', 'Company Number', 'Company Address', 'password']

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# SQLite functions
def add_to_table(dictionay):
    dictionay = dict(dictionay)
    key = tuple(dictionay.keys())
    value = tuple(dictionay.values())

    with conn:
        db.execute("INSERT INTO 'Profiles' " + str(key) + " VALUES " + str(value))




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

    add_to_table(adding_dictionary)
    

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

    with conn:
        company = db.execute("SELECT * FROM 'Profiles' WHERE email = email", #; DELETE ALL DATABASE
                                {'email' : email}).fetchall()
    if len(company) != 1:
        return redirect('/admin_login')
    
    company = company[0]

    if company[4] != password:
        return "Password"
    
    else:
        return "YAYYYYYYYyy"

    




    


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
