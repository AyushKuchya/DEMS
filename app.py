from flask import Flask, render_template, render_template, request
import dbms

app = Flask(__name__)

@app.route('/')
def index():
    x = dbms.hello()
    return x

@app.route('/hello_name')
def hello_name():
    name = request.args.get('name')
    return f'Hello {name}!' if name else 'Hello World'

if __name__ == "__main__":
    app.run(debug=True)