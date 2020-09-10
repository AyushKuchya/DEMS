from flask import Flask, render_template, request, redirect
import sqlite3
from dbms import generate_otp
import smtplib

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if request.method == 'GET':
        return  render_template('register.html')
    else:
        email = request.form.get('answer')
        generate_otp(email)
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