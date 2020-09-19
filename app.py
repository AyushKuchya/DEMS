from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from tempfile import mkdtemp
import sqlite3
from dbms import generate_otp
import smtplib

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'GET':
        return  render_template('register.html')
    else:
        email = request.form.get('answer')
        OTP = generate_otp(email)
        return redirect('/')
        

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')

@app.route('/hello_name')
def hello_name():
    name = request.args.get('name')
    return f'Hello {name}!' if name else 'Hello World'

@app.route('/new_page')
def new_page():
    return 'It\'s lonely in here.'

app.run(debug=True)